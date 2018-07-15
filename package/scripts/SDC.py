from time import sleep
import sys, os, pwd, grp, signal, time, glob, subprocess
from resource_management import *

'''
/**
 * @Script Management StreamSets - daemon
 * @author Tharcisio C. V. Fernandes <tharcisio@cquantt.com>
 */
'''

class Master(Script):
    def install(self, env):
        import params

        service_packagedir = os.path.realpath(__file__).split('/scripts')[0]

        if not os.path.isfile('/etc/sudoers.pre_sdc.bak'):
            Execute('cp /etc/sudoers /etc/sudoers.pre_sdc.bak')
            Execute('echo "'+params.sdc_user+'    ALL=(ALL)       NOPASSWD: ALL" >> /etc/sudoers')

        #Install SDC version 3.3.0-el7
        Execute('rm -rf ' + params.sdc_install_dir, ignore_failures=True)

        Execute('touch ' + params.SDC_LOG_dir + 'sdc-setup.log', ignore_failures=True)

        if params.setup_prebuilt:

            Execute('echo Installing packages')
            
     
            #Fetch and unzip snapshot build, if no cached sdc tar package exists on Ambari server node
            if not os.path.exists(params.temp_file):
                Execute('wget '+params.sdc_download_url+' -O '+params.temp_file+' -a '  + params.sdc_log_file, user=params.sdc_user)
                Execute('tar -zxvf '+params.temp_file+ ' >> ' + params.sdc_log_file, user=params.sdc_user)
                Execute('rm -rf /tmp/streamsets-datacollector-3.3.0-el7-all-rpms/streamsets-datacollector-cdh*', user=params.sdc_user)
                Execute('sudo yum -y localinstall /tmp/streamsets-datacollector-3.3.0-el7-all-rpms/streamsets*.rpm', user=params.sdc_user)
                    
            #update the configs specified by user
            self.configure(env, True)
		
    def stop(self, env):
        print "stop Streamsets..."
        child = subprocess.Popen(['/usr/bin/pgrep', 'sdc'], stdout=subprocess.PIPE)
        result = child.communicate()[0]
        result = result.split('\n')
        pid = result[0]
        Execute('kill -9 ' + pid)
		
    def start(self, env):
        import params
        self.set_conf_bin(env) 
        self.configure(env)

        self.create_hdfs_user(params.sdc_user)

        print "start Streamsets..."
        Execute('service sdc start')
        child = subprocess.Popen(['/usr/bin/pgrep', 'sdc'], stdout=subprocess.PIPE)
        result = child.communicate()[0]
        result = result.split('\n')
        pid = result[0]

        Execute('echo bin dir ' + params.bin_dir)        
        Execute('echo pid file ' + pid)
        if os.path.exists(params.temp_file):
            os.remove(params.temp_file)
		 
    def sdc_status(self, pid):
        from resource_management.core.exceptions import ComponentIsNotRunning
        print "checking status..."
        try:
            if not pid:
                raise ComponentIsNotRunning()
        except Exception, e:
          raise ComponentIsNotRunning()

    def status(self, env): 
        child = subprocess.Popen(['/usr/bin/pgrep', 'sdc'], stdout=subprocess.PIPE)
        result = child.communicate()[0]
        result = result.split('\n')
        pid = result[0]
        self.sdc_status(pid)


    def configure(self, env, isInstall=False):
        import params
        env.set_params(params)

        self.set_conf_bin(env)

        properties_content=InlineTemplate(params.sdc_content)
        File(format("{conf_dir}/sdc.properties"), content=properties_content, owner=params.sdc_user)

    def set_conf_bin(self, env):
        import params
        if params.setup_prebuilt:
          params.conf_dir =  params.sdc_conf_dir
          params.bin_dir =  params.sdc_install_dir+ '/bin'
		
    def restart(self, env):
        import params
        self.set_conf_bin(env) 
        self.configure(env)
        
        print "restart Streamsets..."
        Execute('service sdc restart')

    def create_hdfs_user(self, user):
        Execute('hadoop fs -mkdir -p /user/'+user, user='hdfs', ignore_failures=True)
        Execute('hadoop fs -chown ' + user + ' /user/'+user, user='hdfs')
        Execute('hadoop fs -chgrp ' + user + ' /user/'+user, user='hdfs')

		
if __name__ == "__main__":
    Master().execute()

