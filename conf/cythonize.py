import sys, os, glob

def cythonize(source, includes=(),
              output_h=os.curdir):
    name, ext = os.path.splitext(source)
    output_c = name + '.c'
    #
    from Cython.Compiler.Main import \
         CompilationOptions, default_options, \
         compile, \
         PyrexError
    #
    options = CompilationOptions(default_options)
    options.output_file = output_c
    options.include_path = includes
    #
    from Cython.Compiler import Options
    Options.generate_cleanup_code = 3
    #
    any_failures = 0
    try:
        result = compile(source, options)
        if result.num_errors > 0:
            any_failures = 1
    except (EnvironmentError, PyrexError), e:
        sys.stderr.write(str(e) + '\n')
        any_failures = 1
    if any_failures:
        try:
            os.remove(output_c)
        except OSError:
            pass
        sys.exit(1)
    #
    headers = glob.glob(name+'*.h')
    for header in headers:
        dest = os.path.join(output_h, header)
        try:
            os.remove(dest)
        except OSError:
            pass
        os.rename(header, dest)

def run(source, wdir=os.curdir):
    name = os.path.splitext(source)[0]
    if name.count('.') == 0:
        package = ''
        module  = name
    else:
        bits  = name.split('.')
        package = os.path.join(*bits[:-1])
        module  = bits[-1]
    cwd = os.getcwd()
    os.chdir(wdir)
    try:
        cythonize(source,
                  includes=[os.curdir, 'include'],
                  output_h=os.path.join('include', package),
                  )
    finally:
        os.chdir(cwd)

def docstring_replace(OLD, NEW):
    try:
        from Cython.Compiler.AutoDocTransforms import EmbedSignature
    except ImportError:
        return
    _fmt_signature_orig = EmbedSignature._fmt_signature
    def _fmt_signature(*args, **kwars):
        sig = _fmt_signature_orig(*args, **kwars)
        sig = sig.replace(OLD, NEW); #print sig
        return sig
    EmbedSignature._fmt_signature = _fmt_signature

if __name__ == "__main__":
    docstring_replace(OLD='mpi4py.MPI.', NEW='')
    run('mpi4py.MPI.pyx', 'src')
