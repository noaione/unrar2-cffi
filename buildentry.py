from distutils.command.build import build


class BuildUnrarBeforeBuild(build):
    def run(self):
        self.run_command("build_unrar")
        build.run(self)
