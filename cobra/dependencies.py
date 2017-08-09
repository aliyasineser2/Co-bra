# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as eT
from .log import logger


class Dependencies(object):
    def __init__(self, target_directory):
        """
        :param target_directory: The project's path
        """
        self.directory = target_directory
        self._result = {}
        self._framework = []
        self.dependencies()

    def dependencies(self):
        file_path, flag = self.find_file()
        if flag == 0:  # flag == 0
            logger.warning('Dependency analysis cannot be done without finding dependency files')
        if flag == 1:
            self.find_python_pip(file_path)
        if flag == 2:
            self.find_java_mvn(file_path)

    def find_file(self):
        """
        :return:flag:{1:'python', 2:'java', 3:'oc'}
        """
        flag = 0
        file_path = []
        if os.path.isdir(self.directory):
            for root, dirs, filenames in os.walk(self.directory):
                for filename in filenames:
                    if filename == 'requirements.txt':
                        file_path.append(self.get_path(root, filename))
                        flag = 1
                    if filename == 'pom.xml':
                        file_path.append(self.get_path(root, filename))
                        flag = 2
            return file_path, flag
        else:
            filename = os.path.basename(self.directory)
            if filename == 'requirements.txt':
                flag = 1
                file_path.append(self.directory)
                return file_path, flag
            if filename == 'pom.xml':
                flag = 2
                file_path.append(self.directory)
                return file_path, flag
            return file_path, flag

    @staticmethod
    def get_path(root, filename):
        """
        :param root:
        :param filename:
        :return:
        """
        return os.path.join(root, filename)

    def find_python_pip(self, file_path):
        for requirement in file_path:
            with open(requirement) as fi:
                for line in fi.readlines():
                    flag = line.index("==")
                    module_ = line[:flag]
                    version = line[flag + 2:].strip()
                    self._framework.append(module_)
                    self._result[module_] = version

    def find_java_mvn(self, file_path):
        pom_ns = "{http://maven.apache.org/POM/4.0.0}"
        for pom in file_path:
            tree = self.parse_xml(pom)
            root = tree.getroot()
            childs = root.iter('%sdependency' % pom_ns)
            for child in childs:
                group_id = child.getchildren()[0].text
                artifact_id = child.getchildren()[1].text
                if len(child.getchildren()) > 2:
                    version = child.getchildren()[2].text
                else:
                    version = 'The latest version'
                module_ = artifact_id
                self._framework.append(group_id)
                self._framework.append(artifact_id)
                self._result[module_] = version

    @staticmethod
    def parse_xml(file_path):
        return eT.parse(file_path)

    def get_version(self, module_):
        return self._result[module_]

    @property
    def get_result(self):
        return self._result

    @property
    def get_framework(self):
        return self._framework