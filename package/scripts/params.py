from resource_management import *
from resource_management.libraries.script.script import Script
import sys, os, glob
from resource_management.libraries.functions.version import format_stack_version
from resource_management.libraries.functions.default import default


    
# server configurations
config = Script.get_config()

 
    
# params from sdc-ambari-config
sdc_install_dir = config['configurations']['sdc-ambari-config']['sdc_install_dir']
setup_prebuilt = config['configurations']['sdc-ambari-config']['setup_prebuilt']
sdc_appname = config['configurations']['sdc-ambari-config']['sdc_appname']
sdc_download_url = config['configurations']['sdc-ambari-config']['sdc_download_url']
sdc_conf_dir = config['configurations']['sdc-ambari-config']['sdc_conf_dir']
 

conf_dir=''
bin_dir=''

# params from sdc.properties
sdc_content = config['configurations']['sdc']['sdc.properties']
sdc_user = config['configurations']['sdc-env']['sdc_user']
sdc_group = config['configurations']['sdc-env']['sdc_group']
SDC_LOG_dir = config['configurations']['sdc-env']['SDC_LOG_dir']
sdc_log_file = os.path.join(SDC_LOG_dir,'sdc-setup.log')



temp_file='/tmp/sdc.tgz'