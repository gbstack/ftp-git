import os
import sqlite3

import git


class Application:
    def initDB(self):
        self.db_conn = sqlite3.connect('settings.db')
        cur = self.db_conn.cursor()
        try:
            cur.execute(
                'create table ftp_servers(id integer primary key autoincrement, address varchar(255), username varchar(255), password varchar(255));')
        except sqlite3.OperationalError:
            print('table already exists')

    def getFtpCredentials(self):
        cur = self.db_conn.cursor()
        cur.execute('select * from ftp_servers')
        server = cur.fetchone()
        if server:
            return server
        else:
            return None

    def notifyError(self, text, title='Error'):
        raise NotImplementedError

    def getChangedFiles(self, repo_path):
        # get changed files
        try:
            r = git.Repo(repo_path)
            self.repo_path = repo_path
            self.dir_edit.setText(repo_path)
            self.changed_files_model.clear()
        except git.exc.InvalidGitRepositoryError:
            self.notifyError('Selected path is not a valid git repository')
            return
        c = r.head.commit
        self.changed_files = [os.path.join(self.repo_path, f) for f in list(c.stats.files.keys())]
        for f in list(c.stats.files.keys()):
            print(f)
            self.changed_files_model.appendRow([QStandardItem(f)])
        self.changed_files_table.setColumnWidth(0, self.changed_files_table.width())