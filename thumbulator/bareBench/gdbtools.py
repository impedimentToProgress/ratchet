import gdb
import thumbulator
import time
import os
import re

def get_config(item, config):
  m = re.search('(?<={}=).*'.format(item), config)
  return m.group(0)

def run():
  ###### TEST CONTROLS #####
  f = open('regression.config', 'r') # generated by regression.py, stores the settings for how to run test, how often to fail, logging
  config = f.read()
  f.close()

  mean_cycles_per_lifetime = int(get_config('MEAN', config))
  stdd_cycles_per_lifetime = int(get_config('STDDEV', config))

  root    = get_config('ROOT', config)
  elffile = get_config('ELF', config)
  binfile = get_config('BIN', config)

  logging = get_config('LOGGING', config)
  outdir  = get_config('RESULTS', config)
  simoutfile = get_config('SIMOUT', config)
  logfile = get_config('LOG', config)

  start_sim = True
  #start_sim = False
  sim_path = get_config('SIM', config)
  debug = get_config('DEBUG', config)
  ##########################

  # get the appropriate seed value
  if os.path.isfile(logfile):
    f = open(logfile, 'r')
    log = f.read()
    i = int(log.split(',')[-2])+1
    f.close()
  else:
    i = 0

  resultsout = outdir + '{}.txt'.format(i)

  thumbulator.bp.reset()

  if start_sim:
    outf = open(simoutfile, 'w')
    sim = thumbulator.start_sim(sim_path, binfile, outf)

  time.sleep(1)

  thumbulator.setup(elffile)

  #debug = True
  #debug = False
  #if debug:
  #  thumbulator.tests.replay('error.log',False)
  #else:
  thumbulator.bp.add_bps(resultsout, logging)
  thumbulator.tests.randfreq(i, mean_cycles_per_lifetime, stdd_cycles_per_lifetime)
  if int(debug):
    pass
  else:
    thumbulator.tests.run_til_end(resultsout)

    f = open(logfile, 'a')
    f.write("{},".format(i))
    f.close()

    if start_sim:
      sim.kill()

    gdb.execute('del')

    time.sleep(1)

    gdb.execute('quit')


run()
