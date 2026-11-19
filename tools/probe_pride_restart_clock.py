"""Run the unchanged real-window restart checks against the clock candidate."""
import probe_pride_restart as probe
from audit_scenes import ROOT

if __name__=='__main__':
    probe.BASE=ROOT/'build/pride-restart-clock'
    probe.main()
