from reobase_analysis.tchelpers import *
import reobase_analysis.reobase_utils as ru
from isee_engine.bionet.stimxwaveform import stimx_waveform_factory


el = 409
amp = 0.050
gid = 314900022

example_dir = ru.get_reobase_folder('Run_folder/outputs/dc/', str(gid), dc_folder_format(el,amp,0))
# plot_vext_vm_tiles(example_dir, cell=0, title='$V_m$ and $V_{ext}$ under various inputs')

conf = get_json_from_file(ru.get_config_resolved_path(example_dir, el, amp))
waveform = stimx_waveform_factory(conf)

title = 'Example $V_m$ and $I_{stim}$ for' + ' el {}, cell {}'.format(el, gid)
plot_waveform_vm(example_dir, waveform, cell=0, 
                 title=title)