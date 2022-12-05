import paramiko
import sys
import time
import os
import logging
import datetime as dt
import traceback

host = ""
username = ""
password = ""

time_now = dt.datetime.now()
time_now = dt.datetime.strftime(time_now, "%d-%m-%Y")
current_path = os.getcwd()
log_directory = current_path + '/LOGS/' + str(time_now)

if not os.path.exists(log_directory):
    os.makedirs(log_directory)
    
logging.basicConfig(filename=log_directory + "/fail1.log", filemode= "a",format = "%(asctime)s %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
def reboot(cmd):
    _stdin, result_out,_stderr = client.exec_command(cmd)
    print(result_out.read().decode())
    client.close()
client = paramiko.client.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=username, password=password)

def reboot_fun(host_prefix, reboot_type, node_index=0):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    try:
        status =  ''
        if host_prefix == 'oame':
            _stdin, host_name,_stderr = client.exec_command("hostname")
            hostname = host_name.read().strip()
            print(hostname)
            logger.info(hostname)
            _stdin, date,_stderr = client.exec_command(" date +'%d-%m-%y %T'")
            time1 = date.read().strip()
            print(time1)
            logger.info(time1)
            time.sleep(0.5)
            _stdin, result,_stderr = client.exec_command("ha role")
            status = result.read()
            logger.info(status)
            print(status)
            status = status.strip()

        if host_prefix == 'ddeio':
            hostname ='perfcsd-cb0946-ddeio-0'
            _stdin, date,_stderr = client.exec_command("ssh "+ hostname)
            _stdin, date,_stderr =client.exec_command(" date +'%d-%m-%y %T'")
            time1 = date.read().strip()
            print(time1)
            logger.info(time1)
            _stdin, result_status,_stderr = client.exec_command("ssh "+ hostname + " ha role")
            result_status = (result_status.read().strip())
            print(hostname)
            logger.info(hostname)
            print(result_status)
            logger.info(result_status)
            if result_status == 'ACTIVE':
                    status = result_status
            else:
                hostname ='perfcsd-cb0946-ddeio-1'
                _stdin, date,_stderr = client.exec_command("ssh "+ hostname)
                _stdin, date,_stderr =client.exec_command(" date +'%d-%m-%y %T'")
                time1 = date.read().strip()
                print(time1)
                logger.info(time1)
                _stdin, result_status,_stderr = client.exec_command("ssh "+ hostname + " ha role")
                
                status = (result_status.read()).strip()
                print(hostname)
                logger.info(hostname)
                print(status)
                logger.info(status)
            time.sleep(0.5)
        
        if host_prefix == 'ddeapp':
            hostname = 'perfcsd-cb0946-ddeapp-'+str(node_index)
            _stdin, date,_stderr = client.exec_command("ssh "+ hostname + " date +'%d-%m-%y %T'")
            time1 = date.read().strip()
            print(time1)
            logger.info(time1)
            status = "ACTIVE"
            print(hostname)
            logger.info(hostname)

        if host_prefix == 'db':
            hostname = 'perfcsd-cb0946-db-'+str(node_index)
            _stdin, date,_stderr = client.exec_command("ssh "+ hostname + " date +'%d-%m-%y %T'")
            time1 = date.read().strip()

            print(time1)
            logger.info(time1)
            status = "ACTIVE"
            print(hostname)
            logger.info(hostname)

        if status == "ACTIVE":
            logger.info("enter the loop")
            print("enter the loop")
            if reboot_type == 's':
                logger.info("soft reboot")
                
                if host_prefix == 'oame':
                    _stdin, result,_stderr = client.exec_command('su - ddeadmin --command DDE_status')
                else:
                    _stdin, result,_stderr = client.exec_command("ssh " + hostname + " su - ddeadmin --command DDE_status")
                output = result.read()
                print(output)
                logger.info(output)

            if reboot_type == 'h':
                if host_prefix == 'oame':
                    _stdin, result,_stderr = client.exec_command("/sbin/reboot -f")
                else:
                    _stdin, result,_stderr = client.exec_command("ssh " + hostname + "/sbin/reboot -f")
            
            print("{} rebooted successfully".format(hostname))
            logger.info("{} rebooted successfully".format(hostname))

            after_reboot = validation(host_prefix, hostname)
            after_reb_timestmp = ''
            if host_prefix == 'oame':
                after_reb_timestmp = after_reboot.split(',')[0]
                print("after reboot timestamp for {} is {}".format(hostname, after_reb_timestmp))

            if  host_prefix == 'ddeio':
                after_reb_timestmp = after_reboot.split(',')[0]
                after_reb_timestmp = after_reb_timestmp.split('log:')[1]
                print("after reboot timestamp for {} is {}".format(hostname, after_reb_timestmp))
            
            format_date = "%Y-%m-%d %H:%M:%S"
            time1 = dt.datetime.strptime(time1, "%d-%m-%y %H:%M:%S")
            print(time1)
            
            time2 = dt.datetime.strptime(after_reb_timestmp,format_date)
            print(time2)
            final_timestamp = time1 - time2
            print("final time difference {}".format(final_timestamp))
            client.close()
        else:
            print("error while rebooting..")
    except Exception as err:
        err = traceback.format_exc()
        logger.error(err)
        print(err)

def validation(host_prefix, hostname):
    result = ''
    if host_prefix == "oame":
        _stdin, result,_stderr = client.exec_command(" grep 'setting  role to ACTIVE' /var/log/ha/ha.log | awk 'END{ print }' ")
    elif host_prefix == "ddeio":
        _stdin, result,_stderr = client.exec_command("ssh "+ hostname + " grep 'setting  role to ACTIVE' /var/log/ha/ha.log | awk 'END{ print }' ")
    elif host_prefix == "ddeapp":
        _stdin, result,_stderr = client.exec_command("ssh "+ hostname + " su - ddeadmin --command DDE_status | grep 'Checking App Server...OK' | awk 'END{ print }'")
    elif host_prefix == "db":
        _stdin, result,_stderr = client.exec_command("ssh "+ hostname + " su - ddeadmin --command DDE_status | grep 'Checking Database...OK' | awk 'END{ print }'")

    output = result.read()
    # datetime = datetime.split(',')[0]
    print(output)
    return output

if __name__ == "__main__":
    host_constant = sys.argv[1]
    reboot_par = sys.argv[2]
    index  = sys.argv[3] if len(sys.argv)>=4 else 0
    reboot_fun(host_constant, reboot_par, index)