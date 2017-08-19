from charmhelpers.core import hookenv
from charmhelpers.core import host 
from crontab import CronTab

import configparser
import subprocess
import socket
import tarfile
import os
import datetime


class CouchInfo:
    def __init__(self):
        self.charm_config = hookenv.config()
        self.user = self.charm_config['couch-user']
        self.home_dir = '/home/{}'.format(self.user)
        self.install_dir = self.home_dir + '/CouchPotatoServer'
        self.executable = self.install_dir + '/CouchPotato.py'
        self.config_dir = self.home_dir + '/.couchpotato'
        self.database_dir = self.config_dir + '/database'
        self.settings_file = self.home_dir + '/.couchpotato/settings.conf'
        self.service_name = 'couchpotato.service'
        self.couch_config = configparser.ConfigParser()
        self.couch_config.read(self.settings_file)

    def reload_config(self):
        self.couch_config.read(self.settings_file)

    def save_config(self):
        with open(self.settings_file, 'w') as openFile:
            self.couch_config.write(openFile)

    def set_host(self, hostname):
        self.couch_config['core']['host'] = hostname
        hookenv.log("Couchpotato hostname set to {}".format(hostname), "INFO")

    def set_port(self):
        self.couch_config['core']['port'] = str(self.charm_config['port'])
        hookenv.log("Couchpotato port set to {}".format(self.charm_config['port']), "INFO")

    def set_indexers(self, status):
        if status:
            self.couch_config["newznab"]["enabled"] = "1"
        else:
            self.couch_config["newznab"]["enabled"] = "0"
        hookenv.log("Indexers set to {}".format(status), 'INFO')

    def start(self):
        host.service_start(self.service_name)
        hookenv.log("Starting couchpotato", 'INFO')

    def stop(self):
        host.service_stop(self.service_name)
        hookenv.log("Stoping couchpotato", 'INFO')

    def restart(self):
        host.service_restart(self.service_name)
        hookenv.log("Restarting couchpotato", 'INFO')

    def enable(self):
        subprocess.check_call('systemctl enable {}'.format(self.service_name), shell=True)
        hookenv.log("Couchpotato service enabled", 'INFO')

    def configure_sabnzbd(self, host, port, api_key):
        self.couch_config['sabnzbd']['host'] = '{}:{}'.format(host, port)
        self.couch_config['sabnzbd']['api_key'] = api_key
        self.save_config()

    def configure_plex(self, host, port, user=None, passwd=None):
        self.couch_config['plex']['media_server'] = host
        self.couch_config['plex']['host'] = socket.getfqdn()
        if user:
            self.couch_config['plex']['username'] = user
        if passwd:
            self.couch_config['plex']['password'] = passwd
        self.save_config()

    def set_urlbase(self, urlbase):
        self.couch_config['core']['url_base'] = urlbase
        self.save_config()

    def check_port(self):
        self.reload_config()
        hookenv.log('couch_config port: {}'.format(self.couch_config['core']['port']), 'DEBUG')
        hookenv.log(type(self.couch_config['core']['port']), 'DEBUG')
        hookenv.log('charm_port: {}'.format(self.charm_config['port']), 'DEBUG')
        hookenv.log(type(self.charm_config['port']), 'DEBUG')
        if self.couch_config['core']['port'] != str(self.charm_config['port']):
            hookenv.log('Resetting Couch port to match charm, port should not be'
                        'changed via couchpotato', 'WARNING')
            self.set_port()
            self.save_config()

    def backup(self):
        hookenv.log('Creating backup', 'INFO')
        backup_file = self.charm_config['backup-location'] + '/couchback-{}.tgz'.format(datetime.datetime.now())
        backup_file = backup_file.replace(':', '-')
        try:
            os.mkdir(self.charm_config['backup-location'])
        except FileExistsError:
            pass

        with tarfile.open(backup_file, 'x:gz') as outFile:
            outFile.add(self.database_dir, arcname=self.database_dir.split('/')[-1])
            outFile.add(self.settings_file, arcname=self.settings_file.split('/')[-1])

        # Clean up backups
        if self.charm_config['backup-count'] > 0:
            hookenv.log('Pruning files in {}'.format(self.charm_config['backup-location']), 'INFO')

            def mtime(x): 
                return os.stat(os.path.join(self.charm_config['backup-location'], x)).st_mtime 
            sortedFiles = sorted(os.listdir(self.charm_config['backup-location']), key=mtime)
            deleteCount = max(len(sortedFiles) - self.charm_config['backup-count'], 0)
            for file in sortedFiles[0:deleteCount]:
                os.remove(os.path.join(self.charm_config['backup-location'], file))
        else:
            hookenv.log('Skipping backup pruning', 'INFO')

    def create_backup_cron(self):
        self.remove_backup_cron(log=False)
        system_cron = CronTab(user='root')
        unit = hookenv.local_unit()
        directory = hookenv.charm_dir()
        action = directory + '/actions/backup' 
        command = "juju-run {unit} {action}".format(unit=unit, action=action)
        job = system_cron.new(command=command, comment="couchpotato backup")
        job.setall(self.charm_config['backup-cron'])
        system_cron.write()
        hookenv.log("Backup created for: {}".format(self.charm_config['backup-cron']))
    
    def remove_backup_cron(self, log=True):
        system_cron = CronTab(user='root')
        try:
            job = next(system_cron.find_comment("couchpotato backup"))
            system_cron.remove(job)
            system_cron.write()
            if log:
                hookenv.log("Removed backup cron.", 'INFO')
        except StopIteration:
            if log:
                hookenv.log("Backup removal called, but cron not present.", 'WARNING')

