import sys, os, glob

def cythonize(source, includes=(),
              output_h=os.curdir):
    name, ext = os.path.splitext(source)
    output = name.replace('.', '_')
    #
    from Cython.Compiler.Main import \
         CompilationOptions, default_options, \
         compile, \
         PyrexError
    #
    options = CompilationOptions(default_options)
    options.output_file = output  + '.c'
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
            os.remove(output  + '.c')
        except OSError:
            pass
        sys.exit(1)
    #
    headers = glob.glob(output+'*.h')
    for header in headers:
        dest = os.path.join(output_h, header)
        try:
            os.remove(dest)
        except OSError:
            pass
        os.rename(header, dest)

def run(source, wdir):
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
                  includes=[os.curdir, 'include',
                            os.path.join('include', package)],
                  output_h=os.path.join('include', package),
                  )
    finally:
        os.chdir(cwd)

if __name__ == "__main__":
    run('mpi4py.MPI.pyx', 'src')
