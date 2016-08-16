#!/usr/bin/python
#coding=utf-8

"""
auth:zhengyingying
mail:zhengyingying@playcrab.com
createtime:2015-10-13 10:00:00
usege: 用于生成etl_data 任务

"""

import datetime,time,os
from custom.command import Custom_Command as cmd
from addtask.base import BaseAddTask
from addtask.centerapp import CenterApp

__ALL__=['AddFile2MysqlTask']
class AddFile2MysqlTask(BaseAddTask,CenterApp):
    
    def __init__(self):
        BaseAddTask.__init__(self)
        CenterApp.__init__(self)
    
    def make_task_log(self,tasks,log_date,log_time,do_rate='hour'):
        '''
            把需要存储的任务加入列表
        '''
        #task_log = []
        for task in tasks:
            if task['column_name'] is None:
                continue
            task_ip = self.get_platform_ip(task['flag'],task['game'],task['platform'])
            for ip in task_ip:
                prefix_sql = '' if task['prefix_sql'] is None else str(task['prefix_sql'])
                post_sql = '' if task['post_sql'] is None else str(task['post_sql'])

                log_info = task['game']+"\t"+task['platform']+"\t"+ip+"\t"+task['log_name']+"\t"+task['log_dir']+"\t"\
                           +task['md5_name']+"\t"+task['md5_dir']+"\t"+task['download_url']+"\t"\
                           +str(len(task['column_name'].split(',')))+"\t"+task['do_rate']+"\t"\
                           +str(task['group'])+"\t"+str(task['priority'])+"\t"+str(task['from_id'])+"\t"\
                           +str(task['target_id'])+"\t"+prefix_sql+"\t"+str(task['load_sql'])+"\t"+post_sql+"\t"\
                           +str(log_date.strftime('%Y%m%d'))+"\t"+str(log_time)+"\t"+str(log_date.strftime('%Y%m%d'))
                #print log_info
                output = open('/data/add_data/file2mysql_'+str(time.strftime("%Y%m%d",time.localtime()))+'.txt', 'a')
                output.write(str(log_info)+"\n")
                output.close()

        #         log_info = [task['game'],task['platform'],ip,task['log_name'],task['log_dir'],
        #                     task['md5_name'],task['md5_dir'],task['download_url'],len(task['column_name'].split(",")),
        #                     task['do_rate'],task['group'],task['priority'],task['from_id'],task['target_id'],task['prefix_sql'],task['load_sql'],task['post_sql'],log_date.strftime('%Y%m%d'),log_time,log_date.strftime('%Y%m%d')]
        #         task_log.append(tuple(log_info))
        #
        #         if len(task_log) == 1000:
        #             self.save_task(task_log)
        #             task_log = []
        #
        # self.save_task(task_log)

    def save_task(self, logtime):
        result = self.mysql.load("load data local infile '/data/add_data/file2mysql_"+logtime+".txt' into table etl_manage.file2mysql_log(game,platform,source_ip,log_name,log_dir,md5_name,md5_dir,download_url,col_num,do_rate,\`group\`,priority,from_id,target_id,prefix_sql,load_sql,post_sql,log_date,log_time,task_date);")
        return result


    # def save_task(self,param):
    #     '''
    #         存储
    #     '''
    #     sql = 'INSERT INTO file2mysql_log \
    #     (`game`,`platform`,`source_ip`,`log_name`,`log_dir`,`md5_name`,`md5_dir`,`download_url`,`col_num`,`do_rate`,`group`,`priority`,`from_id`,`target_id`,`prefix_sql`,`load_sql`,`post_sql`,`log_date`,`log_time`,`task_date`) \
    #     VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    #     self.mysql.executemany(sql,param)
    #     self.mysql.commit()
        
if __name__ == '__main__':
    task = AddFile2MysqlTask()
    print "start add file2mysql task"
    print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    logtime = str(time.strftime("%Y%m%d", time.localtime()))

    #排除同名文件存在的可能，为重复执行清理障碍
    if os.path.exists('/data/add_data/file2mysql_'+logtime+'.txt'):
        cmd.run('rm -f /data/add_data/file2mysql_'+logtime+'.txt')

    ip_list = task.get_ip_list()
    #拼接任务
    task.get_task('select etl.*,s.column_name,s.flag from etl_data etl left join structure s on etl.target_id = s.id where etl.type = "load" and etl.db_type = "mysql" and etl.is_delete = 0',ip_list)

    #调用存储 load 文件
    if task.save_task(logtime)['status'] != 0:
        print "data insert error"

    task.close_mysql()
    print "stop add file2mysql task"
    print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
