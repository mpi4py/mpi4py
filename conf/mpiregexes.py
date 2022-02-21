import re

def anyof(*args):
    return r'(?:%s)' % '|'.join(args)

def join(*args):
    tokens = []
    for tok in args:
        if isinstance(tok, (list, tuple)):
            tok = '(%s)' % r'\s*'.join(tok)
        tokens.append(tok)
    return r'\s*'.join(tokens)

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

basic_type    = r'(?:void|int|char\s*\*{1,3})'
integral_type = r'MPI_(?:Aint|Offset|Count|Fint)'
struct_type   = r'MPI_(?:Status|F08_status)'
opaque_type   = r'MPI_(?:Datatype|Request|Message|Op|Info|Group|Errhandler|Session|Comm|Win|File)'
any_mpi_type  = r'(?:%s|%s|%s)' % (struct_type, integral_type, opaque_type)

upper_name  = r'MPI_[A-Z0-9_]+'
camel_name  = r'MPI_[A-Z][a-z0-9_]+'
usrfun_name = camel_name + r'_(?:function|function_c|fn)'

arg_list = r'.*'
ret_type = r'void|int|double|MPI_Aint'

canyint = anyof(r'int', r'long(?:\s+long)?')
canyptr = join(r'\w+', pointer+'?')

annotation = r'\#\:\='
fallback_value = r'\(?[A-Za-z0-9_\+\-\(\)\*]+\)?'
fallback = r'(?:%s)?' % join (annotation, [fallback_value])

INTEGRAL_TYPE = join( typedef, [canyint], [integral_type], fallback, eol)
STRUCT_TYPE   = join( struct,  [struct_type], colon+opt, fallback,  eol)
OPAQUE_TYPE   = join( typedef, canyptr,  [opaque_type], eol)
FUNCTION_TYPE = join( typedef, [ret_type], [camel_name], lparen, [arg_list], rparen, fallback, eol)

ENUM_VALUE      = join(sol, enum, [upper_name], fallback, eol)
HANDLE_VALUE    = join(sol, [opaque_type], [upper_name], fallback, eol)
BASIC_PTRVAL    = join(sol, [basic_type,  pointer], [upper_name], fallback, eol)
INTEGRAL_PTRVAL = join(sol, [integral_type, pointer], [upper_name], fallback, eol)
STRUCT_PTRVAL   = join(sol, [struct_type, pointer], [upper_name], fallback, eol)
FUNCT_PTRVAL    = join(sol, [usrfun_name, pointer], [upper_name], fallback, eol)
FUNCTION_PROTO  = join(sol, [ret_type], [camel_name], lparen, [arg_list], rparen, fallback, eol)

fint_type = r'MPI_Fint'
fmpi_type = opaque_type.replace('Datatype', 'Type')
c2f_name  = fmpi_type+'_c2f'
f2c_name  = fmpi_type+'_f2c'

FUNCTION_C2F = join(sol, [fint_type],   [c2f_name], lparen, [opaque_type], rparen, fallback, eol)
FUNCTION_F2C = join(sol, [opaque_type], [f2c_name], lparen, [fint_type],   rparen, fallback, eol)


IGNORE = anyof(join(sol, r'cdef.*', eol),
               join(sol, struct, r'_mpi_\w+_t', eol),
               join(sol, 'int', r'MPI_(?:SOURCE|TAG|ERROR)', eol),
               join(sol, r'#.*', eol),
               join(sol, eol))

# compile the RE's
glb = globals()
all = [key for key in dict(glb) if key.isupper()]
for key in all: glb[key] = re.compile(glb[key])
