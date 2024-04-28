# Very, very naive RE-based way for collecting declarations inside
# 'cdef extern from *' Cython blocks in in source files, and next
# generate compatibility headers for partially implemented MPIs.

# ruff: noqa: E501

import re
from textwrap import indent, dedent
import warnings

def anyof(*args):
    return r'(?:{})'.format('|'.join(args))

def join(*args):
    tokens = []
    for tok in args:
        if isinstance(tok, (list, tuple)):
            tok = '({})'.format(r'\s*'.join(tok))
        tokens.append(tok)
    return r'\s*'.join(tokens)

def r_(*args):
    return re.compile(join(*args))

lparen   = r'\('
rparen   = r'\)'
colon    = r'\:'
asterisk = r'\*'
ws       = r'\s*'
sol      = r'^'
eol      = r'$'
opt      = r'?'

enum    = join('enum', colon)
typedef = 'ctypedef'
pointer = asterisk
struct  = join(typedef, 'struct')

integral_type_names = [
    'Aint',
    'Offset',
    'Count',
    'Fint',
]

struct_type_names = [
    'Status',
    'F08_status',
]

handle_type_names = [
    'Datatype',
    'Request',
    'Message',
    'Op',
    'Info',
    'Group',
    'Errhandler',
    'Session',
    'Comm',
    'Win',
    'File',
]

basic_type    = r'(?:void|int|char\s*\*{1,3})'
integral_type = r'MPI_(?:{})'.format('|'.join(integral_type_names))
struct_type   = r'MPI_(?:{})'.format('|'.join(struct_type_names))
opaque_type   = r'MPI_(?:{})'.format('|'.join(handle_type_names))

upper_name  = r'MPI_[A-Z0-9_]+'
camel_name  = r'MPI_[A-Z][a-z0-9_]+'
usrfun_name = camel_name + r'_(?:function|function_c|fn)'

arg_list = r'.*'
ret_type = r'void|int|double|MPI_Aint'

canyint = anyof(r'int', r'long(?:\s+long)?')
canyptr = join(r'\w+', pointer+'?')

annotation = r'\#\:\='
fallback_value = r'\(?[A-Za-z0-9_\+\-\(\)\*]+\)?'
fallback = rf'(?:{join(annotation, [fallback_value])})?'

fint_type = r'MPI_Fint'
fmpi_type = opaque_type.replace('Datatype', 'Type')
c2f_name  = fmpi_type+'_c2f'
f2c_name  = fmpi_type+'_f2c'


class Re:

    INTEGRAL_TYPE   = r_(sol, typedef, [canyint], [integral_type], fallback, eol)
    STRUCT_TYPE     = r_(sol, struct,  [struct_type], colon+opt, fallback,  eol)
    OPAQUE_TYPE     = r_(sol, typedef, canyptr,  [opaque_type], eol)
    FUNCTION_TYPE   = r_(sol, typedef, [ret_type], [camel_name], lparen, [arg_list], rparen, fallback, eol)

    ENUM_VALUE      = r_(sol, enum, [upper_name], fallback, eol)
    HANDLE_VALUE    = r_(sol, [opaque_type], [upper_name], fallback, eol)
    BASIC_PTRVAL    = r_(sol, [basic_type,  pointer], [upper_name], fallback, eol)
    INTEGRAL_PTRVAL = r_(sol, [integral_type, pointer], [upper_name], fallback, eol)
    STRUCT_PTRVAL   = r_(sol, [struct_type, pointer], [upper_name], fallback, eol)
    FUNCTION_PTRVAL = r_(sol, [usrfun_name, pointer], [upper_name], fallback, eol)
    FUNCTION_PROTO  = r_(sol, [ret_type], [camel_name], lparen, [arg_list], rparen, fallback, eol)

    FUNCTION_C2F    = r_(sol, [fint_type],   [c2f_name], lparen, [opaque_type], rparen, fallback, eol)
    FUNCTION_F2C    = r_(sol, [opaque_type], [f2c_name], lparen, [fint_type],   rparen, fallback, eol)

    IGNORE = r_(anyof(
        join(sol, r'cdef.*', eol),
        join(sol, struct, r'_mpi_\w+_t', eol),
        join(sol, 'int', r'MPI_(?:SOURCE|TAG|ERROR)', eol),
        join(sol, r'#.*', eol),
        join(sol, eol),
    ))


class Node:

    REGEX = None

    @classmethod
    def match(self, line):
        m = self.REGEX.match(line)
        return m.groups() if m else None

    HEADER = None
    CONFIG = None
    MISSING = None

    MISSING_HEAD = """\
    #ifndef PyMPI_HAVE_%(name)s
    #undef  %(cname)s
    """
    MISSING_TAIL = """
    #endif

    """

    def init(self, name, **kwargs):
        self.name = name
        self.__dict__.update(kwargs)

    def header(self):
        line = dedent(self.HEADER) % vars(self)
        line = line.replace('\n', '')
        line = line.replace('  ', ' ')
        return line + '\n'

    def config(self):
        return dedent(self.CONFIG) % vars(self)

    def missing(self, guard=True):
        if guard:
            head = dedent(self.MISSING_HEAD)
            tail = dedent(self.MISSING_TAIL)
        else:
            head = '#undef  %(cname)s\n'
            tail = '\n\n'
        body = dedent(self.MISSING)
        return (head+body+tail) % vars(self)

class NodeType(Node):
    CONFIG = """\
    %(ctype)s v; %(ctype)s* p; (void)v; (void)p;"""

    def __init__(self, ctype):
        self.init(name=ctype,
                  cname=ctype,
                  ctype=ctype,)

class NodeStructType(NodeType):
    HEADER = """\
    typedef struct {%(cfields)s ...; } %(ctype)s;"""
    MISSING = """\
    typedef struct PyMPI_%(ctype)s {
    %(cfields)s
    } PyMPI_%(ctype)s;
    #define %(ctype)s PyMPI_%(ctype)s"""

    def __init__(self, ctype, cfields):
        super().__init__(ctype)
        self.cfields = '\n'.join(
            [f'  {ctype} {cname};' for ctype, cname in cfields]
        )

class NodeFuncType(NodeType):
    HEADER = """\
    typedef %(crett)s (%(cname)s)(%(cargs)s);"""
    MISSING = """\
    typedef %(crett)s (MPIAPI PyMPI_%(cname)s)(%(cargs)s);
    #define %(cname)s PyMPI_%(cname)s"""

    def __init__(self, crett, cname, cargs, calias=None):
        self.init(name=cname,
                  cname=cname,
                  ctype=cname+'*',)
        self.crett = crett
        self.cargs = cargs or 'void'
        if calias is not None:
            self.MISSING = '#define %(cname)s %(calias)s'
            self.calias = calias

class NodeValue(Node):
    HEADER = """\
    const %(ctype)s %(cname)s;"""
    CONFIG = """\
    %(ctype)s v; v = %(cname)s; (void)v;"""
    MISSING = '#define %(cname)s (%(calias)s)'

    def __init__(self, ctype, cname, calias):
        self.init(name=cname,
                  cname=cname,
                  ctype=ctype,
                  calias=calias)
        if ctype.endswith('*'):
            ctype = ctype + ' const'
            self.HEADER = ctype + ' %(cname)s;'

class NodePtrVal(NodeValue):
    MISSING = '#define %(cname)s ((%(ctype)s)%(calias)s)'

def ctypefix(ct):
    ct = ct.replace('[][3]',' (*)[3]')
    ct = ct.replace('[]','*')
    return ct

class NodeFuncProto(Node):
    HEADER = """\
    %(crett)s %(cname)s(%(cargs)s);"""
    CONFIG = """\
    %(crett)s v; v = %(cname)s(%(cargscall)s); (void)v;"""
    MISSING = ' '. join(['#define %(cname)s(%(cargsnamed)s)',
                        'PyMPI_UNAVAILABLE("%(name)s"%(comma)s%(cargsnamed)s)'])
    def __init__(self, crett, cname, cargs, calias=None):
        self.init(name=cname, cname=cname)
        self.crett = crett
        self.cargs = cargs or 'void'
        if cargs == 'void':
            cargs = ''
        if cargs:
            cargs = [c.strip() for c in cargs.split(',')]
            if cargs[-1] == '...':
                del cargs[-1]
        else:
            cargs = []
        self.cargstype = cargs
        nargs = len(cargs)
        self.comma = ',' if nargs else ''
        cargscall = [f'({ctypefix(a)})0' for a in cargs]
        self.cargscall = ','.join(cargscall)
        cargsnamed = ['a%d' % (a+1) for a in range(nargs)]
        self.cargsnamed = ','.join(cargsnamed)
        if calias is not None:
            self.MISSING = '#define %(cname)s %(calias)s'
            self.calias = calias

class IntegralType(NodeType):
    REGEX = Re.INTEGRAL_TYPE
    HEADER = """\
    typedef %(cbase)s... %(ctype)s;"""
    MISSING = """\
    typedef %(ctdef)s PyMPI_%(ctype)s;
    #define %(ctype)s PyMPI_%(ctype)s"""
    def __init__(self, cbase, ctype, calias=None):
        super().__init__(ctype)
        self.cbase = cbase
        if calias is not None:
            self.ctdef = calias
        else:
            self.ctdef = cbase

class StructType(NodeStructType):
    REGEX = Re.STRUCT_TYPE
    def __init__(self, ctype, calias=None):
        cfields = []
        if ctype == 'MPI_Status':
            cnames = ['MPI_SOURCE', 'MPI_TAG', 'MPI_ERROR']
            cfields = list(zip(['int']*3, cnames))
        super().__init__(ctype, cfields)
        if calias is not None:
            self.MISSING = '#define %(cname)s %(calias)s'
            self.calias = calias

class OpaqueType(NodeType):
    REGEX = Re.OPAQUE_TYPE
    HEADER = """\
    typedef struct{...;} %(ctype)s;"""
    MISSING = """\
    typedef void *PyMPI_%(ctype)s;
    #define %(ctype)s PyMPI_%(ctype)s"""

class FunctionType(NodeFuncType):
    REGEX = Re.FUNCTION_TYPE

class EnumValue(NodeValue):
    REGEX = Re.ENUM_VALUE
    def __init__(self, cname, calias):
        self.init(name=cname,
                  cname=cname,
                  ctype='int',
                  calias=calias)

class HandleValue(NodeValue):
    REGEX = Re.HANDLE_VALUE
    MISSING = '#define %(cname)s ((%(ctype)s)%(calias)s)'

class BasicPtrVal(NodePtrVal):
    REGEX = Re.BASIC_PTRVAL

class IntegralPtrVal(NodePtrVal):
    REGEX = Re.INTEGRAL_PTRVAL

class StructPtrVal(NodePtrVal):
    REGEX = Re.STRUCT_PTRVAL

class FunctionPtrVal(NodePtrVal):
    REGEX = Re.FUNCTION_PTRVAL

class FunctionProto(NodeFuncProto):
    REGEX = Re.FUNCTION_PROTO

class FunctionC2F(NodeFuncProto):
    REGEX = Re.FUNCTION_C2F
    MISSING = ' '.join(['#define %(cname)s(%(cargsnamed)s)',
                       '((void)%(cargsnamed)s,(%(crett)s)0)'])

class FunctionF2C(NodeFuncProto):
    REGEX = Re.FUNCTION_F2C
    MISSING = ' '.join(['#define %(cname)s(%(cargsnamed)s)',
                       '((void)%(cargsnamed)s,%(cretv)s)'])
    def __init__(self, *a, **k):
        NodeFuncProto.__init__(self, *a, **k)
        self.cretv =  self.crett.upper() + '_NULL'

class Generator:

    NODE_TYPES = [
        IntegralType,
        StructType, OpaqueType,
        HandleValue, EnumValue,
        BasicPtrVal,
        IntegralPtrVal, StructPtrVal,
        FunctionType, FunctionPtrVal,
        FunctionProto, FunctionC2F, FunctionF2C,
        ]

    def __init__(self):
        self.nodes = []
        self.nodemap = {}

    def parse_file(self, filename):
        with open(filename) as f:
            self.parse_lines(f)

    def parse_lines(self, lines):
        for line in lines:
            self.parse_line(line)

    def parse_line(self, line):
        if Re.IGNORE.match(line):
            return
        nodemap  = self.nodemap
        nodelist = self.nodes
        for nodetype in self.NODE_TYPES:
            args = nodetype.match(line)
            if args:
                node = nodetype(*args)
                nodemap[node.name] = len(nodelist)
                nodelist.append(node)
                break
        if not args:
            warnings.warn(f'unmatched line:\n{line}', stacklevel=1)

    def __iter__(self):
        return iter(self.nodes)

    def __getitem__(self, name):
        return self.nodes[self.nodemap[name]]

    def dump_header_h(self, fileobj):
        if isinstance(fileobj, str):
            with open(fileobj, 'w') as f:
                self.dump_header_h(f)
            return
        for node in self:
            fileobj.write(node.header())

    CONFIG_HEAD = """\
    #ifndef PyMPI_PYMPICONF_H
    #define PyMPI_PYMPICONF_H

    """
    CONFIG_MACRO = 'PyMPI_HAVE_%s'
    CONFIG_TAIL = """\

    #endif /* !PyMPI_PYMPICONF_H */
    """
    def dump_config_h(self, fileobj, suite):
        if isinstance(fileobj, str):
            with open(fileobj, 'w') as f:
                self.dump_config_h(f, suite)
            return
        head  = dedent(self.CONFIG_HEAD)
        macro = dedent(self.CONFIG_MACRO)
        tail  = dedent(self.CONFIG_TAIL)
        fileobj.write(head)
        if suite is None:
            for node in self:
                line = '#undef %s\n' % (macro % node.name)
                fileobj.write(line)
        else:
            for name, result in suite:
                if result:
                    line = '#define %s 1\n' % (macro % name)
                else:
                    line = '#undef  %s\n' % (macro % name)
                fileobj.write(line)
        fileobj.write(tail)

    MISSING_HEAD = """\
    #ifndef PyMPI_MISSING_H
    #define PyMPI_MISSING_H

    #ifndef PyMPI_UNUSED
    # if defined(__GNUC__)
    #   define PyMPI_UNUSED __attribute__ ((__unused__))
    # else
    #   define PyMPI_UNUSED
    # endif
    #endif

    #define PyMPI_ERR_UNAVAILABLE (-1431655766) /*0xAAAAAAAA*/

    static PyMPI_UNUSED
    int PyMPI_UNAVAILABLE(const char *name,...)
    { (void)name; return PyMPI_ERR_UNAVAILABLE; }

    """
    MISSING_TAIL = """\
    #endif /* !PyMPI_MISSING_H */
    """
    def dump_missing_h(self, fileobj, suite):
        if isinstance(fileobj, str):
            with open(fileobj, 'w') as f:
                self.dump_missing_h(f, suite)
            return
        head = dedent(self.MISSING_HEAD)
        tail = dedent(self.MISSING_TAIL)
        #
        fileobj.write(head)
        if suite is None:
            for node in self:
                fileobj.write(node.missing())
        else:
            for name, result in suite:
                node = self[name]
                if not result:
                    fileobj.write(node.missing())
        fileobj.write(tail)


    LARGECNT_HEAD = """\
    #ifndef PyMPI_LARGECNT_H
    #define PyMPI_LARGECNT_H

    #include <stdlib.h>
    #include <string.h>
    #ifndef PyMPI_MALLOC
      #define PyMPI_MALLOC malloc
    #endif
    #ifndef PyMPI_FREE
      #define PyMPI_FREE free
    #endif
    #ifndef PyMPI_MEMCPY
      #define PyMPI_MEMCPY memcpy
    #endif

    #define PyMPIAllocArray(dsttype, dst, len)                       \\
      do {                                                           \\
          size_t _m = (size_t) (len) * sizeof(dsttype);              \\
          (dst) = (dsttype *) PyMPI_MALLOC(_m ? _m : 1);             \\
      } while (0)                                                 /**/

    #define PyMPIFreeArray(dst)                                      \\
      do {                                                           \\
        if ((dst) != NULL) PyMPI_FREE(dst);                          \\
        (dst) = NULL; (void) (dst);                                  \\
      } while (0)                                                 /**/

    #define PyMPICastError(ERRORCODE)                                \\
      do {                                                           \\
        ierr = (ERRORCODE);                                          \\
        (void) MPI_Comm_call_errhandler(MPI_COMM_SELF, ierr);        \\
        goto fn_exit;                                                \\
      } while (0)                                                 /**/

    #define PyMPICastValue(dsttype, dst, srctype, src)               \\
      do {                                                           \\
        (dst) = (dsttype) (src);                                     \\
        if ((srctype) (dst) != (src))                                \\
          PyMPICastError(MPI_ERR_ARG);                               \\
      } while (0)                                                 /**/

    #define PyMPICastArray(dsttype, dst, srctype, src, len)          \\
      do {                                                           \\
        (dst) = NULL;                                                \\
        if ((src) != NULL) {                                         \\
          MPI_Aint _n = (MPI_Aint) (len), _i;                        \\
          PyMPIAllocArray(dsttype, dst, len);                        \\
          if ((dst) == NULL)                                         \\
            PyMPICastError(MPI_ERR_OTHER);                           \\
          for (_i = 0; _i < _n; _i++) {                              \\
            (dst)[_i] = (dsttype) (src)[_i];                         \\
            if ((srctype) (dst)[_i] != (src)[_i]) {                  \\
              PyMPIFreeArray(dst);                                   \\
              PyMPICastError(MPI_ERR_ARG);                           \\
            }                                                        \\
          }                                                          \\
        }                                                            \\
      } while (0)                                                 /**/

    #define PyMPIMoveArray(dsttype, dst, srctype, src, len)          \\
      do {                                                           \\
        if ((src) != NULL && (dst) != NULL) {                        \\
          size_t _n = (size_t) (len);                                \\
          unsigned char *_buf = (unsigned char *) (src);             \\
          (void) PyMPI_MEMCPY(_buf, (dst), _n * sizeof(dsttype));    \\
          PyMPI_FREE(dst); (dst) = (dsttype *) _buf;                 \\
        }                                                            \\
      } while (0)                                                 /**/

    #define PyMPICommSize(comm, n)                                   \\
      do {                                                           \\
        int _inter = 0;                                              \\
        ierr = MPI_Comm_test_inter(comm, &_inter);                   \\
        if (_inter)                                                  \\
          ierr = MPI_Comm_remote_size((comm), &(n));                 \\
        else                                                         \\
          ierr = MPI_Comm_size((comm), &(n));                        \\
        if (ierr != MPI_SUCCESS) goto fn_exit;                       \\
      } while (0)                                                 /**/

    #define PyMPICommLocGroupSize(comm, n)                           \\
      do {                                                           \\
        ierr = MPI_Comm_size((comm), &(n));                          \\
        if (ierr != MPI_SUCCESS) goto fn_exit;                       \\
      } while (0)                                                 /**/

    #define PyMPICommNeighborCount(comm, ns, nr)                     \\
      do {                                                           \\
        int _topo = MPI_UNDEFINED;                                   \\
        int _i, _n; (ns) = (nr) = 0;                                 \\
        ierr = MPI_Topo_test((comm), &_topo);                        \\
        if (ierr != MPI_SUCCESS) goto fn_exit;                       \\
        if (_topo == MPI_UNDEFINED) {                                \\
          ierr = MPI_Comm_size((comm), &_n);                         \\
          (ns) = (nr) = _n;                                          \\
        } else if (_topo == MPI_CART) {                              \\
          ierr = MPI_Cartdim_get((comm), &_n);                       \\
          (ns) = (nr) = 2 * _n;                                      \\
        } else if (_topo == MPI_GRAPH) {                             \\
          ierr = MPI_Comm_rank((comm), &_i);                         \\
          ierr = MPI_Graph_neighbors_count(                          \\
                   (comm), _i, &_n);                                 \\
          (ns) = (nr) = _n;                                          \\
        } else if (_topo == MPI_DIST_GRAPH) {                        \\
          ierr = MPI_Dist_graph_neighbors_count(                     \\
                   (comm), &(nr), &(ns), &_i);                       \\
        }                                                            \\
        if (ierr != MPI_SUCCESS) goto fn_exit;                       \\
      } while (0)                                                 /**/

    """

    LARGECNT_BEGIN = """\
    #ifndef PyMPI_HAVE_%(name)s_c
    static int Py%(name)s_c(%(argsdecl)s)
    {
    """

    LARGECNT_COLLECTIVE = """\
    PyMPICommSize(a%(commid)d, n);
    """

    LARGECNT_LOCGROUP = """\
    PyMPICommLocGroupSize(a%(commid)d, n);
    """

    LARGECNT_NEIGHBOR = """\
      PyMPICommNeighborCount(a%(commid)d, ns, nr);
    """

    LARGECNT_CALL = """\
    ierr = %(name)s(%(argscall)s);
    if (ierr != MPI_SUCCESS) goto fn_exit;
    """

    LARGECNT_END = """\
      return ierr;
    }
    #undef  %(name)s_c
    #define %(name)s_c Py%(name)s_c
    #endif
    """

    LARGECNT_TAIL = """\
    #endif /* !PyMPI_LARGECNT_H */
    """

    LARGECNT_RE = re.compile(r'^mpi_({})_c$'.format('|'.join([
        r'(i?(b|s|r|p)?send(_init)?(recv(_replace)?)?)',
        r'(i?m?p?recv(_init)?)',
        r'(buffer_(at|de)tach|get_count)',
        r'(i?(bcast|gather(v)?|scatter(v?)|all(gather(v)?|toall(v|w)?))(_init)?)',
        r'(i?((all)?reduce(_local|(_scatter(_block)?)?)|(ex)?scan)(_init)?)',
        r'(i?neighbor_all(gather(v)?|toall(v|w)?)(_init)?)',
        r'(win_(create|allocate(_shared)?|shared_query))',
        r'(r?(put|get|(get_)?accumulate))',
        r'file_(((i)?(read|write).*)|get_type_extent)',
    ])))

    def dump_largecnt_h(self, fileobj):
        if isinstance(fileobj, str):
            with open(fileobj, 'w') as f:
                self.dump_largecnt_h(f)
            return

        def largecount_functions():
            for node in self:
                name = node.name
                if self.LARGECNT_RE.match(name.lower()):
                    yield name[:-2]

        def declare(t, v, init=None):
            t = t.strip()
            if t.endswith('[]'):
                t = t[:-2].strip()
                code = f'{t} *{v}'
            elif t.endswith('*'):
                t = t[:-1].strip()
                code = f'{t} *{v}'
            else:
                code = f'{t} {v}'
            if init is not None:
                code += f' = {init}'
            return code

        def generate(name):
            is_neighbor = 'neighbor' in name.lower()
            is_nonblocking = name.startswith('MPI_I')
            node1 = self[name+'_c']
            node2 = self[name]

            cargstype1 = node1.cargstype
            cargstype2 = node2.cargstype
            argstype = list(zip(cargstype1, cargstype2))

            convert_array = False
            for (t1, t2) in argstype:
                if t1 != t2:
                    if t1 == 'MPI_Count[]' and t2 == 'int[]':
                        convert_array = True
                        break
                    if t1 == 'MPI_Aint[]'  and t2 == 'int[]':
                        convert_array = True
                        break
            commid = None
            if convert_array:
                for i, (t1, _) in enumerate(argstype, start=1):
                    if t1 == 'MPI_Comm':
                        commid = i
                        break

            dtypeidx = 0
            argslist = []
            argsinit = []
            argstemp = []
            argsconv = []
            argscall = []
            argsoutp = []
            argsfree = []

            CASTVALUE = 'PyMPICastValue(%s, b%d, %s, a%d)'
            CASTARRAY = 'PyMPICastArray(%s, b%d, %s, a%d, %s)'
            MOVEARRAY = 'PyMPIMoveArray(%s, b%d, %s, a%d, %s)'
            FREEARRAY = 'PyMPIFreeArray(b%d)'

            argsinit += ['int ierr']
            if commid is not None:
                if is_neighbor:
                    argsinit += ['int ns, nr']
                else:
                    argsinit += ['int n']
            for i, (t1, t2) in enumerate(argstype, start=1):
                argslist += [declare(t1, 'a%d' % i)]
                if t1.startswith('MPI_Datatype'):
                    dtypeidx += 1
                if t1 == t2:
                    argscall += ['a%d' % i]
                else:
                    if t1.endswith('[]'):
                        t1, t2, n = t1[:-2], t2[:-2], 'n'
                        argstemp += [declare(t2, '*b%d' % i, 'NULL')]
                        if is_neighbor:
                            n = ('ns', 'nr')[dtypeidx]
                        subs = (t2, i, t1, i, n)
                        argsconv += [CASTARRAY % subs]
                        if is_nonblocking:
                            argsconv += [MOVEARRAY % subs]
                        else:
                            argsfree += [FREEARRAY % i]
                        argscall += ['b%d' % i]
                    elif t1.endswith('*'):
                        t1, t2 = t1[:-1], t2[:-1]
                        pinit = 'a%d ? &b%d : NULL' % (i, i)
                        argstemp += [declare(t2, 'b%d' % i, 0)]
                        argstemp += [declare(t2+'*', 'p%d' % i, pinit)]
                        argscall += ['p%d' % i]
                        argsoutp += ['if (a%d) *a%d = b%d' % (i, i, i)]
                    else:
                        subs = (t2, i, t1, i)
                        argstemp += [declare(t2, 'b%d' % i)]
                        argsconv += [CASTVALUE % subs]
                        argscall += ['b%d' % i]

            tab = '  '
            subs = {
                'name':     name,
                'argsdecl': (',\n'+' '*(len(name)+20)).join(argslist),
                'argscall': ', '.join(argscall),
                'commid':   commid,
            }
            begin = self.LARGECNT_BEGIN % subs
            if commid is None:
                setup = ''
            elif is_neighbor:
                setup = self.LARGECNT_NEIGHBOR % subs
            elif 'reduce_scatter' in name.lower():
                setup = self.LARGECNT_LOCGROUP % subs
            else:
                setup = self.LARGECNT_COLLECTIVE % subs
            call = self.LARGECNT_CALL % subs
            end = self.LARGECNT_END % subs

            yield dedent(begin)
            yield indent('{};\n'.format('; '.join(argsinit)), tab)
            yield indent('{};\n'.format('; '.join(argstemp)), tab)
            yield indent(dedent(setup), tab)
            for line in argsconv:
                yield indent(f'{line};\n', tab)
            yield indent(dedent(call), tab)
            for line in argsoutp:
                yield indent(f'{line};\n', tab)
            yield indent('fn_exit:\n', tab[:-1])
            for line in argsfree:
                yield indent(f'{line};\n', tab)
            yield dedent(end)
            yield '\n'

        head = dedent(self.LARGECNT_HEAD)
        tail = dedent(self.LARGECNT_TAIL)
        self.largecnt = 0
        fileobj.write(head)
        for name in largecount_functions():
            self.largecnt += 1
            for code in generate(name):
                fileobj.write(code)
        fileobj.write(tail)

# -----------------------------------------

if __name__ == '__main__':
    import os
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='MPI API generator')
    parser.add_argument('-q', '--quiet', action='store_true')
    parser.add_argument('-l', '--list', action='store_true')
    args = parser.parse_args()

    if args.list:
        args.quiet = True

    def log(message):
        if not args.quiet:
            print(message)

    generator = Generator()
    libmpi_pxd = os.path.join('src', 'mpi4py', 'libmpi.pxd')
    log(f'parsing file {libmpi_pxd}')
    generator.parse_file(libmpi_pxd)
    log('processed %d definitions' % len(generator.nodes))

    if args.list:
        for node in generator:
            print(node.name)
        sys.exit(0)

    #config_h  = os.path.join('src', 'lib-mpi', 'pympiconf.h')
    #log('writing file %s' % config_h)
    #generator.dump_config_h(config_h, None)

    missing_h = os.path.join('src', 'lib-mpi', 'missing.h')
    log(f'writing file {missing_h}')
    generator.dump_missing_h(missing_h, None)

    largecnt_h = os.path.join('src', 'lib-mpi', 'largecnt.h')
    log(f'writing file {largecnt_h}')
    generator.dump_largecnt_h(largecnt_h)
    log('generated %d large count fallbacks' % generator.largecnt)

    #libmpi_h = os.path.join('.', 'libmpi.h')
    #log('writing file %s' % libmpi_h)
    #generator.dump_header_h(libmpi_h)

# -----------------------------------------
