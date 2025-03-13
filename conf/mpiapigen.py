# Very, very naive RE-based way for collecting declarations inside
# 'cdef extern from *' Cython blocks in in source files, and next
# generate compatibility headers for partially implemented MPIs.

# ruff: noqa: E501, UP031

import glob
import os
import sys
from re import compile as re_compile
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
    return re_compile(join(*args))

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

cint_type = r'int'
cmpi_type = opaque_type.replace('Datatype', 'Type')
h2i_name = cmpi_type+'_toint'
i2h_name = cmpi_type+'_fromint'

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

    FUNCTION_PROTO  = r_(sol, [ret_type],  [camel_name], lparen, [arg_list],    rparen, fallback, eol)
    FUNCTION_H2I    = r_(sol, [cint_type],   [h2i_name], lparen, [opaque_type], rparen, fallback, eol)
    FUNCTION_I2H    = r_(sol, [opaque_type], [i2h_name], lparen, [cint_type],   rparen, fallback, eol)
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

FALLBACK = {
    'MPI_Aint_add': '(a0,a1) ((MPI_Aint)((char*)(a0)+(a1)))',
    'MPI_Aint_diff': '(a0,a1) ((MPI_Aint)((char*)(a0)-(char*)(a1)))',
    'MPI_Wtime': '() 0.0',
    'MPI_Wtick': '() 0.0',
}

class NodeFuncProto(Node):
    HEADER = """\
    %(crett)s %(cname)s(%(cargs)s);"""
    CONFIG = """\
    %(crett)s v; v = %(cname)s(%(cargscall)s); (void)v;"""
    MISSING = ' '. join([
        '#define %(cname)s(%(cargsnamed)s)',
        'PyMPI_UNAVAILABLE("%(name)s"%(comma)s%(cargsnamed)s)',
    ])
    def __init__(self, crett, cname, cargs, calias=None):
        self.init(name=cname, cname=cname)
        self.crett = crett
        self.cargs = cargs or 'void'
        if cargs == 'void':
            cargs = ''
        if cargs:
            cargs = [c.strip() for c in cargs.split(',')]
        else:
            cargs = []
        self.cargstype = cargs[:]
        cargs = [a for a in cargs if a != '...']
        nargs = len(cargs)
        self.comma = ',' if nargs else ''
        cargscall = [f'({ctypefix(a)})0' for a in cargs]
        self.cargscall = ','.join(cargscall)
        cargsnamed = ['a%d' % (a+1) for a in range(nargs)]
        self.cargsnamed = ','.join(cargsnamed)
        if calias is not None:
            self.calias = calias
            self.MISSING = '#define %(cname)s %(calias)s'
        elif cname in FALLBACK:
            self.MISSING = '#define %(cname)s' + FALLBACK[cname]

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

class FunctionH2I(NodeFuncProto):
    REGEX = Re.FUNCTION_H2I
    MISSING="""\
    #ifdef  PyMPI_HAVE_%(fallback)s
    #define %(cname)s(%(cargsnamed)s) ((%(crett)s)%(fallback)s(%(cargsnamed)s))
    #else
    #define %(cname)s(%(cargsnamed)s) ((void)%(cargsnamed)s,%(cretv)s)
    #endif"""
    def __init__(self, *a, **k):
        NodeFuncProto.__init__(self, *a, **k)
        self.fallback = self.name.replace('_toint', '_c2f')
        self.cretv = f'({self.crett})-1'

class FunctionI2H(NodeFuncProto):
    REGEX = Re.FUNCTION_I2H
    MISSING="""\
    #ifdef  PyMPI_HAVE_%(fallback)s
    #define %(cname)s(%(cargsnamed)s) (%(fallback)s((%(cargs)s)%(cargsnamed)s))
    #else
    #define %(cname)s(%(cargsnamed)s) ((void)%(cargsnamed)s,%(cretv)s)
    #endif"""
    def __init__(self, *a, **k):
        NodeFuncProto.__init__(self, *a, **k)
        self.fallback = self.name.replace('_fromint', '_f2c')
        self.cretv = f'({self.crett})0'

class FunctionC2F(NodeFuncProto):
    REGEX = Re.FUNCTION_C2F
    MISSING = FunctionH2I.MISSING
    def __init__(self, *a, **k):
        NodeFuncProto.__init__(self, *a, **k)
        self.fallback = self.name.replace('_c2f', '_toint')
        self.cretv = f'({self.crett})-1'

class FunctionF2C(NodeFuncProto):
    REGEX = Re.FUNCTION_F2C
    MISSING = FunctionI2H.MISSING
    def __init__(self, *a, **k):
        NodeFuncProto.__init__(self, *a, **k)
        self.fallback = self.name.replace('_f2c', '_fromint')
        self.cretv = f'({self.crett})0'

class Generator:

    PROLOG = f"""\
    /* Generated with `python conf/{os.path.basename(__file__)}` */
    """

    NODE_TYPES = [
        IntegralType,
        StructType,
        OpaqueType,
        FunctionType,
        HandleValue,
        EnumValue,
        BasicPtrVal,
        IntegralPtrVal,
        StructPtrVal,
        FunctionPtrVal,
        FunctionH2I,
        FunctionI2H,
        FunctionC2F,
        FunctionF2C,
        FunctionProto,
    ]

    def __init__(self):
        self.nodes = []
        self.nodemap = {}
        self.stdapi = {}

    def parse_stdapi(self, filename):
        dirname = os.path.dirname(filename)
        header = re_compile(
            r'^\s*#include\s+"mpi-(\d\d)\.h"\s*$'
        )
        define = re_compile(
            r'^\s*#define\s*PyMPI_HAVE_(MPI_[A-Za-z0-9_]+)\s+1\s*$'
        )
        with open(filename) as f:
            for line in f:
                m = header.match(line)
                if m is None:
                    continue
                numversion = int(m.groups()[0])
                version = (numversion // 10, numversion % 10)
                self.stdapi[version] = symlist = []
                with open(os.path.join(dirname, f"mpi-{numversion}.h")) as h:
                    for line in h:
                        m = define.match(line)
                        if m is None:
                            continue
                        symbol = m.groups()[0]
                        index = self.nodemap.get(symbol)
                        if index is None:
                            continue
                        node = self.nodes[index]
                        node.version = version
                        symlist.append(symbol)
        for a, la in self.stdapi.items():
            for b, lb in self.stdapi.items():
                if a != b:
                    common = set(la).intersection(set(lb))
                    if common:
                        raise AssertionError(f"{a} & {b} -> {common}")

    def parse_file(self, filename):
        with open(filename) as f:
            self.parse_lines(f)

    def parse_lines(self, lines):
        for line in lines:
            self.parse_line(line)

    def parse_line(self, line):
        if '# Deprecated' in line:
            self.deprecated = True
            return
        elif Re.IGNORE.match(line):
            self.deprecated = False
            return
        nodemap  = self.nodemap
        nodelist = self.nodes
        deprecated = getattr(self, 'deprecated', False)
        for nodetype in self.NODE_TYPES:
            args = nodetype.match(line)
            if args:
                node = nodetype(*args)
                nodemap[node.name] = len(nodelist)
                nodelist.append(node)
                node.deprecated = deprecated
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

    #endif /* PyMPI_PYMPICONF_H */
    """
    def dump_config_h(self, fileobj, suite):
        if isinstance(fileobj, str):
            with open(fileobj, 'w') as f:
                self.dump_config_h(f, suite)
            return
        prlg  = dedent(self.PROLOG)
        head  = dedent(self.CONFIG_HEAD)
        macro = dedent(self.CONFIG_MACRO)
        tail  = dedent(self.CONFIG_TAIL)
        fileobj.write(prlg)
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

    MISSING_HEAD = """
    """
    MISSING_TAIL = """\
    /* */
    """
    def dump_missing_h(self, fileobj, suite=None):
        if isinstance(fileobj, str):
            with open(fileobj, 'w') as f:
                self.dump_missing_h(f, suite)
            return
        prlg = dedent(self.PROLOG)
        head = dedent(self.MISSING_HEAD)
        tail = dedent(self.MISSING_TAIL)
        #
        fileobj.write(prlg)
        fileobj.write(head)
        if suite is None:
            for name in (
                'MPI_Status_c2f',
                'MPI_Status_f2c',
                'MPI_Type_create_f90_integer',
                'MPI_Type_create_f90_real',
                'MPI_Type_create_f90_complex',
            ):
                fileobj.write(dedent(f"""\
                #ifdef PyMPI_MISSING_{name}
                #undef PyMPI_HAVE_{name}
                #endif
                \n"""))
            for node in self:
                fileobj.write(node.missing())
        else:
            for name, result in suite:
                node = self[name]
                if not result:
                    fileobj.write(node.missing())
        fileobj.write(tail)


    LARGECNT_HEAD = """
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

    #define PyMPICommLocalGroupSize(comm, n)                         \\
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
    #if !defined(PyMPI_HAVE_%(name)s_c) || PyMPI_LEGACY_ABI
    #undef %(name)s_c
    """

    LARGECNT_DECLARE = """\
    static int Py%(name)s_c(%(argsdecl)s)
    {
      PyMPI_WEAK_CALL(%(name)s_c, %(argsorig)s);
      {
    """

    LARGECNT_COLLECTIVE = """\
    PyMPICommSize(a%(commid)d, n);
    """

    LARGECNT_LOCALGROUP = """\
    PyMPICommLocalGroupSize(a%(commid)d, n);
    """

    LARGECNT_NEIGHBOR = """\
      PyMPICommNeighborCount(a%(commid)d, ns, nr);
    """

    LARGECNT_CALL = """\
    ierr = %(callname)s(%(argscall)s);
    if (ierr != MPI_SUCCESS) goto fn_exit;
    """

    LARGECNT_RETURN = """\
      return ierr;
      }
    }
    """

    LARGECNT_END = """\
    #undef  %(name)s_c
    #define %(name)s_c Py%(name)s_c
    #endif
    """

    LARGECNT_TAIL = """\
    /* */
    """

    LARGECNT_RE = re_compile(r'^mpi_({})_c$'.format('|'.join([
        r'type_(contiguous|vector|indexed|create|size|get_(true_)?extent).*',
        r'(get|status_set)_elements|get_count',
        r'(pack|unpack)(_external)?(_size)?',
        r'(i?(b|s|r|p)?send(_init)?(recv(_replace)?)?)',
        r'(i?m?p?recv(_init)?)',
        r'(buffer_(at|de)tach)|(comm|session)_(at|de)tach_buffer',
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
            subname = name[4:].lower()
            is_neighbor = 'neighbor' in subname
            is_nonblocking = name.startswith('MPI_I')
            is_datatype = subname.startswith('type_')
            is_packunpack = any(map(subname.startswith, ('pack', 'unpack')))
            is_packunpack_size = is_packunpack and subname.endswith('_size')

            node1 = self[name + '_c']
            node2 = self[name]
            try:
                node2 = self[name + '_x']
            except KeyError:
                pass
            callname = node2.name

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
            argsorig = []
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
                argsorig += ['a%d' % i]
                if t1.startswith('MPI_Datatype'):
                    dtypeidx += 1
                if t1 == t2:
                    argscall += ['a%d' % i]
                else:
                    if t1.endswith('[]'):
                        t1, t2, n = t1[:-2], t2[:-2], 'n'
                        argstemp += [declare(t2, '*b%d' % i, 'NULL')]
                        if is_datatype:
                            is_darray = name.endswith('_darray')
                            n = 'a1' if not is_darray else 'a3'
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
                        if is_packunpack and not is_packunpack_size:
                            subs = (t2, i, t1, f'a{i} ? *a{i} : 0')
                            castvalue = CASTVALUE.replace('a%d', '%s')
                            argsconv += [castvalue % subs]
                    else:
                        subs = (t2, i, t1, i)
                        argstemp += [declare(t2, 'b%d' % i)]
                        argsconv += [CASTVALUE % subs]
                        argscall += ['b%d' % i]

            tab = '  '
            subs = {
                'name':     name,
                'callname': callname,
                'argsdecl': (',\n'+' '*(len(name)+20)).join(argslist),
                'argsorig': ', '.join(argsorig),
                'argscall': ', '.join(argscall),
                'commid':   commid,
            }
            begin = self.LARGECNT_BEGIN % subs
            fdecl = self.LARGECNT_DECLARE % subs
            if commid is None:
                setup = ''
            elif is_neighbor:
                setup = self.LARGECNT_NEIGHBOR % subs
            elif 'reduce_scatter' in name.lower():
                setup = self.LARGECNT_LOCALGROUP % subs
            else:
                setup = self.LARGECNT_COLLECTIVE % subs
            call = self.LARGECNT_CALL % subs
            ret = self.LARGECNT_RETURN % subs
            end = self.LARGECNT_END % subs

            yield dedent(begin)
            yield dedent(fdecl)
            if argsinit:
                yield indent('{};\n'.format('; '.join(argsinit)), tab)
            if argstemp:
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
            yield dedent(ret)
            yield dedent(end)
            yield '\n'

        prlg = dedent(self.PROLOG)
        head = dedent(self.LARGECNT_HEAD)
        tail = dedent(self.LARGECNT_TAIL)
        self.largecnt = 0
        fileobj.write(prlg)
        fileobj.write(head)
        for name in largecount_functions():
            self.largecnt += 1
            for code in generate(name):
                fileobj.write(code)
        fileobj.write(tail)

    MPIABI_HEAD = """
    #define _pympi_CALL(fn, ...) \\
    PyMPI_WEAK_CALL(fn, __VA_ARGS__); \\
    return _pympi__##fn(__VA_ARGS__)
    """
    MPIABI_TAIL = """
    #undef _pympi_CALL
    /* */
    """

    def dump_mpiabi_h(self, fileobj, std=True):
        if isinstance(fileobj, str):
            with open(fileobj, 'w') as f:
                self.dump_mpiabi_h(f, std)
            return

        def funcargs(node):
            argsdecl, argscall = [], []
            for i, t in enumerate(node.cargstype):
                if t == '...':
                    argsdecl.append(t)
                else:
                    try:
                        p = t.index('[')
                    except ValueError:
                        p = len(t)
                    t, a = t[:p], t[p:]
                    argsdecl.append(f'{t} a{i}{a}')
                    argscall.append(f'a{i}')
            if node.name in ('MPI_Status_c2f', 'MPI_Status_f2c'):
                if not argsdecl[0].startswith('const '):
                    argsdecl[0] = 'const ' + argsdecl[0]
            argsdecl = ','.join(argsdecl) if argsdecl else 'void'
            argscall = ','.join(argscall) if argscall else ''
            return (argsdecl, argscall)

        def abi_function(node, fallback=None, guard=True):
            name = node.name

            rtype = node.crett
            rvalue = f'PyMPI_UNAVAILABLE("{name}")'
            if rtype != 'int':
                rvalue = f'(({rtype})0)'
            rvalue = getattr(node, 'cretv', rvalue)
            argsdecl, argscall = funcargs(node)

            pympi0 = f'{name}'
            pympi1 = f'_pympi_{name}'
            fsign0 = f'{rtype} {pympi0}({argsdecl})'
            fsign1 = f'{rtype} {pympi1}({argsdecl})'
            fbody1 = f'{{ _pympi_CALL({name},{argscall}); }}'

            undef = dedent(f"""
            #undef {name}
            """)
            if guard:
                declare = dedent(f"""\
                #ifndef PyMPI_HAVE_{name}
                PyMPI_EXTERN {fsign0};
                #endif
                """)
            else:
                declare = dedent(f"""\
                PyMPI_EXTERN {fsign0};
                """)

            if fallback is None:
                pympiname = f'_pympi__{name}'
                fallback = dedent(f"""\
                #define {pympiname}(...) {rvalue}
                """)
            override = dedent(f"""\
            PyMPI_LOCAL {fsign1} {fbody1}
            #define {name} {pympi1}
            """)
            return [undef, declare, fallback, override]

        def abi_handle_openmpi(node):
            name = node.name.lower()
            oname = f'ompi_{name}'
            if node.ctype == 'MPI_Datatype':
                if oname in (
                    'ompi_mpi_long_long',  # ompi_mpi_long_long_int
                    'ompi_mpi_c_complex',  # ompi_mpi_c_float_complex
                ):
                    return ""
                for old, new in (
                    ('complex', 'cplex'),
                    ('double_complex', 'dblcplex'),
                    ('double_precision', 'dblprec'),
                    ('long_double_int', 'longdbl_int'),
                    ('cxx_float_complex', 'cxx_cplex'),
                    ('cxx_double_complex', 'cxx_dblcplex'),
                    ('cxx_long_double_complex', 'cxx_ldblcplex'),
                ):
                    if oname == f'ompi_mpi_{old}':
                        oname = f'ompi_mpi_{new}'
            if node.ctype == 'MPI_Op':
                if not oname.endswith('_null'):
                    oname = oname.replace('_mpi_', '_mpi_op_')
            for htype in ('message', 'request'):
                if name.startswith(f'mpi_{htype}_'):
                    oname = f'o{name}'
            if node.ctype == 'MPI_Session':
                oname = oname.replace('session', 'instance')
            return dedent(f"""\
            PyMPI_WEAK_LOAD({oname})
            """)

        mpi_version_min = (5, 0) if std else (3, 0)
        mpi_version_max = (5, 0)

        ftnconv = []
        intconv = []
        handles = []
        fstatus = []
        fortran = []
        aintops = []
        functions = []
        for node in self:
            if node.deprecated:
                continue
            if isinstance(node, (FunctionH2I, FunctionI2H)):
                intconv.append(node)
                continue
            if isinstance(node, (FunctionC2F, FunctionF2C)):
                ftnconv.append(node)
                continue
            if isinstance(node, HandleValue):
                handles.append(node)
                continue
            if isinstance(node, FunctionProto):
                if node.name in ('MPI_Status_c2f', 'MPI_Status_f2c'):
                    fstatus.append(node)
                    continue
                if node.name.startswith('MPI_Type_create_f90_'):
                    fortran.append(node)
                    continue
                if node.name in ('MPI_Aint_add', 'MPI_Aint_diff'):
                    aintops.append(node)
                    continue
                functions.append(node)
                continue

        prlg = dedent(self.PROLOG)
        head = dedent(self.MPIABI_HEAD)
        tail = dedent(self.MPIABI_TAIL)
        fileobj.write(prlg)
        fileobj.write(head)

        if not std:
            fileobj.write(dedent("""
            #ifdef OPEN_MPI
            """))
            for node in handles:
                code = abi_handle_openmpi(node)
                fileobj.write(code)
            fileobj.write(dedent("""\
            #endif /* OPEN_MPI */
            """))

        if not std:
            fileobj.write(dedent("""
            #ifdef MPICH
            """))
            for node in fortran:
                for code in abi_function(node):
                    fileobj.write(code)
            fileobj.write(dedent("""
            #endif /* MPICH */
            """))

        if not std:
            argdcl = {'c': 'MPI_Status *c', 'f': 'MPI_Fint *f'}
            argval = {'c': '*c', 'f': '*(MPI_Status *)(char *)f'}
            for node in fstatus:
                name = node.name
                pympiname = f'_pympi__{name}'
                a, _, b = name[-3:].partition('2')
                args = f'(const {argdcl[a]}, {argdcl[b]})'
                copy = f'({argval[b]} = {argval[a]})'
                ok, err = 'MPI_SUCCESS', 'MPI_ERR_ARG'
                body = f'{{ return (c && f) ? {copy}, {ok} : {err}; }}'
                impl = dedent(f"""\
                static int {pympiname}{args} {body}
                """)
                for code in abi_function(node, impl, guard=False):
                    fileobj.write(code)
            for node in ftnconv:
                name = node.name
                pympiname = f'_pympi__{name}'
                rtype = node.crett
                rval_o = node.cretv
                rval_m = f'({rtype})arg'
                if name.startswith('MPI_File_'):
                    rval_m = node.cretv
                impl = dedent(f"""\
                #ifdef MPICH
                #define {pympiname}(arg) ({rval_m})
                #else
                #define {pympiname}(arg) ({rval_o})
                #endif
                """)
                for code in abi_function(node, impl, guard=False):
                    fileobj.write(code)
        if not std:
            for node in intconv:
                name = node.name
                pympiname = f'_pympi__{name}'
                if node.crett == 'int':
                    rtype, atype = '(int)', ''
                else:
                    rtype, atype = '', '(int)'
                body = f'{rtype}{node.fallback}({atype}arg)'
                impl = dedent(f"""\
                #define {pympiname}(arg) {body}
                """)
                for code in abi_function(node, impl):
                    fileobj.write(code)

        if not std:
            for node in aintops:
                name = node.name
                pympiname = f'_pympi__{name}'
                rtype = node.crett
                argsdecl, argscall = funcargs(node)
                signature = f'{rtype} {pympiname}({argsdecl})'
                expr1 = f'{name}({argscall})'
                expr2 = FALLBACK[name].partition(' ')[2]
                impl = dedent(f"""
                #ifdef {name}
                static {signature} {{ return {expr1}; }}
                #else
                static {signature} {{ return {expr2}; }}
                #endif
                """)
                code = abi_function(node, impl, guard=False)
                undef, declare, fallback, override = code
                code = [fallback, undef.lstrip(), declare, override]
                while code:
                    fileobj.write(code.pop(0))

        outdir = os.path.dirname(fileobj.name)
        wildcard = os.path.join(outdir, 'mpiapi??.h')
        undef_re = re_compile(r'^\s*#undef\s+(MPI_.*)\s*$')
        implemented = set()
        for header in glob.glob(wildcard):
            with open(header) as f:
                for line in f:
                    match = undef_re.match(line)
                    if match:
                        implemented.add(match.group(1))
        for node in functions:
            if node.name.endswith('_c'):
                implemented.add(node.name)
        implemented.discard('MPI_Op_create_c')

        for node in functions:
            if node.version <= mpi_version_min:
                continue
            if node.version >= mpi_version_max:
                continue
            code = abi_function(node)
            fileobj.write(code.pop(0))
            fileobj.write(code.pop(0))
            if node.name not in implemented:
                while code:
                    fileobj.write(code.pop(0))

        fileobj.write(tail)



# -----------------------------------------

if __name__ == '__main__':
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
    mpiapi_h = os.path.join('src', 'lib-mpi', 'config', 'mpiapi.h')
    log(f'parsing file {mpiapi_h}')
    generator.parse_stdapi(mpiapi_h)
    log('processed %d definitions' % sum(map(len, generator.stdapi.values())))

    if args.list:
        for node in generator:
            print(node.name)
        sys.exit(0)

    #config_h  = os.path.join('src', 'lib-mpi', 'pympiconf.h')
    #log('writing file %s' % config_h)
    #generator.dump_config_h(config_h, None)

    missing_h = os.path.join('src', 'lib-mpi', 'missing.h')
    log(f'writing file {missing_h}')
    generator.dump_missing_h(missing_h)

    mpiabi0_h = os.path.join('src', 'lib-mpi', 'mpiabi0.h')
    log(f'writing file {mpiabi0_h}')
    generator.dump_mpiabi_h(mpiabi0_h, std=False)

    mpiabi1_h = os.path.join('src', 'lib-mpi', 'mpiabi1.h')
    log(f'writing file {mpiabi1_h}')
    generator.dump_mpiabi_h(mpiabi1_h, std=True)

    largecnt_h = os.path.join('src', 'lib-mpi', 'largecnt.h')
    log(f'writing file {largecnt_h}')
    generator.dump_largecnt_h(largecnt_h)
    log('generated %d large count fallbacks' % generator.largecnt)

    #libmpi_h = os.path.join('.', 'libmpi.h')
    #log('writing file %s' % libmpi_h)
    #generator.dump_header_h(libmpi_h)

# -----------------------------------------
