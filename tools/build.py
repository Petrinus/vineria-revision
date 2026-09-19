"""Build the shared site, then apply the approved transparent artwork treatment."""
import runpy
runpy.run_path('tools/build_base.py', run_name='__main__')
runpy.run_path('tools/refine.py', run_name='__main__')
