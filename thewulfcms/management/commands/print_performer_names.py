import datetime

from django.core.management.base import BaseCommand
from optparse import make_option

from thewulfcms.models import Event


class Command(BaseCommand):
	option_list = BaseCommand.option_list + (
		make_option(
			"--season_year",
			help="the year '20XX' of the starting season."
			),
		)

	def handle(self, *args, **options):
		print "writing performer and composer names to /home/mwinter80/tmp/performers.txt"
		year = int(options["season_year"])
		this_season_start = datetime.date(year, 9, 1)
		evs = Event.objects.filter(start_date__gte=this_season_start)
		with open("/home/mwinter80/tmp/performers.txt", "w") as thefile:
			names = set()
			for ev in evs.iterator():
				perfs = ev.performer_set.all()
				progrs = ev.program_set.all()
				for perf in perfs:
					profiles = perf.performer.users.all()
					for profile in profiles:
						names.add(profile.get_full_name().title())
				for prog in progrs:
					works = prog.works.all()
					for work in works:
						authors = work.authors.all()
						for author in authors:
							profiles = author.users.all()
							for profile in profiles:
								names.add(profile.get_full_name().title())
			for name in names:
				try:
					thefile.write(name)
					thefile.write(", ")
				except UnicodeEncodeError:
					print "error writing:", name
		print "done!"
