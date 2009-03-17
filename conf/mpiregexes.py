import re

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
eol      = r'$'

enum    = join('enum', colon)
typedef = 'ctypedef'
pointer = asterisk
struct  = join(typedef, 'struct')

basic_type    = r'(?:void|int|char\s*\*{1,3})'
struct_type   = r'MPI_(?:Status)'
integral_type = r'MPI_(?:Aint|Offset)'
opaque_type   = r'MPI_(?:Datatype|Request|Op|Info|Group|Errhandler|Comm|Win|File)'
any_mpi_type  = r'(?:%s|%s|%s)' % (struct_type, integral_type, opaque_type)

upper_name  = r'MPI_[A-Z0-9_]+'
camel_name  = r'MPI_[A-Z][a-z0-9_]+'
usrfun_name = camel_name + r'_(?:function|fn)'

arg_list = r'.*'
ret_type = r'void|int|double'


canylong = join(r'long', r'(?:long)?')
canyptr  = join(r'\w+', pointer+'?')

annotation = r'\#\:\='
defval = r'(?:%s)?' % join (annotation, [r'\(?[A-Za-z0-9_\+\-\(\)\*]+\)?'])

STRUCT_TYPE   = join( struct,  [struct_type] , colon,  eol)
INTEGRAL_TYPE = join( typedef, canylong, [integral_type], eol)
OPAQUE_TYPE   = join( typedef, canyptr,  [opaque_type],   eol)
FUNCTION_TYPE = join( typedef, [ret_type], [camel_name],
                      lparen, [arg_list], rparen,
                      defval, eol)

ENUM_VALUE     = join( enum,          [upper_name], defval, eol)
HANDLE_VALUE   = join( [opaque_type], [upper_name], defval, eol)
BASICP_VALUE   = join( [basic_type,  pointer], [upper_name], defval , eol)
STRUCTP_VALUE  = join( [struct_type, pointer], [upper_name], defval , eol)
FUNCTP_VALUE   = join( [usrfun_name, pointer], [upper_name], defval , eol)
FUNCTION_PROTO = join([ret_type], [camel_name],
                      lparen, [arg_list], rparen,
                      defval, eol)

fint_type = r'MPI_Fint'
c2f_name  = r'MPI_[A-Z][a-z_]+_c2f'
f2c_name  = r'MPI_[A-Z][a-z_]+_f2c'

FINT_TYPE    = join( typedef, canylong, [fint_type], eol)
FINTP_VALUE  = join( [fint_type, pointer], [upper_name], defval , eol)
FUNCTION_C2F = join([fint_type], [c2f_name],
                    lparen, [opaque_type], rparen,
                    defval, eol)
FUNCTION_F2C = join([opaque_type], [f2c_name],
                    lparen, [fint_type], rparen,
                    defval, eol)


# compile the RE's
glb = globals()
all = [key for key in dict(glb) if key.isupper()]
for key in all: glb[key] = re.compile(glb[key])
