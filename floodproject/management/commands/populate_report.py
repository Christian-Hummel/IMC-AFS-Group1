from django.core.management.base import BaseCommand
from ...models import Report

class Command(BaseCommand):
    help = 'populates the database with test report data'

    """
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    lon = models.FloatField()
    lat = models.FloatField()
    user_id = models.ForeignKey(CustomUser, null=False, on_delete=models.CASCADE, default=1)
    date = models.DateTimeField(auto_now=True)
    """
    def handle(self, *args, **options):

        report1 = Report(title="General observation of lost cars",
                         description="Many just were taken to some other place by the flood by today afternoon",
                         lon=15.174722, lat=48.170556, user_id=1)
        report2 = Report(title="Emergency situation: No way out",
                         description="Flood cut off escape routes, we have limited amounts of food left", lon=15.641111,
                         lat=48.145556, user_id=2)
        report3 = Report(title="Bridge under water", description="The bridge connecting to the town is submerged",
                         lon=15.929444, lat=48.555556, user_id=3)
        report4 = Report(title="Collapsed house", description="Several homes collapsed due to heavy flooding",
                         lon=16.158889, lat=48.465278, user_id=4)
        report5 = Report(title="Evacuation halted",
                         description="Rising water levels forced the evacuation process to stop abruptly",
                         lon=15.891667, lat=48.204167, user_id=5)
        report6 = Report(title="Livestock stranded", description="Farmers report livestock stranded on higher ground",
                         lon=15.8725, lat=48.014167, user_id=6)
        report7 = Report(title="Unreachable villages",
                         description="Multiple villages are completely unreachable by road", lon=15.931944,
                         lat=48.141667, user_id=7)
        report8 = Report(title="Temporary shelter set up",
                         description="A temporary shelter has been established in the nearby school", lon=15.8775,
                         lat=48.192778, user_id=8)
        report9 = Report(title="Damaged crops", description="Floodwaters have ruined the crops in the valley",
                         lon=15.981944, lat=48.215556, user_id=9)
        report10 = Report(title="Overturned vehicles", description="Several vehicles overturned due to strong currents",
                          lon=16.042222, lat=48.271389, user_id=10)
        report11 = Report(title="Electricity outage", description="Power outages reported in multiple areas",
                          lon=15.749167, lat=48.325833, user_id=11)
        report12 = Report(title="Rescue boats deployed", description="Rescue teams have deployed boats for evacuation",
                          lon=15.731389, lat=48.390833, user_id=12)
        report13 = Report(title="Flooded hospital",
                          description="The town hospital is flooded and patients need evacuation", lon=16.022222,
                          lat=48.411389, user_id=13)
        report14 = Report(title="Animals swept away", description="Wild animals swept away in the flood", lon=15.684167,
                          lat=48.332778, user_id=14)
        report15 = Report(title="Dam about to burst",
                          description="The dam is at critical levels and might burst anytime", lon=15.8275,
                          lat=48.238611, user_id=15)
        report16 = Report(title="Relief supplies delayed", description="Relief trucks stuck due to blocked roads",
                          lon=15.883611, lat=48.362222, user_id=16)
        report17 = Report(title="Collapsed bridge", description="Another bridge collapsed under the force of water",
                          lon=16.112778, lat=48.503611, user_id=17)
        report18 = Report(title="Residents stranded on rooftops",
                          description="People are stranded on rooftops awaiting rescue", lon=15.804722, lat=48.420278,
                          user_id=18)
        report19 = Report(title="Blocked drainage", description="Drainage systems clogged and overflowing",
                          lon=15.672222, lat=48.144444, user_id=19)
        report20 = Report(title="Medical supplies running low",
                          description="Medical supplies in shelters are running low", lon=15.921111, lat=48.154444,
                          user_id=20)
        report21 = Report(title="Floodwaters receding slowly", description="Floodwaters are receding but very slowly",
                          lon=16.078333, lat=48.176111, user_id=21)
        report22 = Report(title="Collapsed power lines",
                          description="Downed power lines posing a risk of electrocution", lon=15.981944, lat=48.435556,
                          user_id=22)
        report23 = Report(title="Communication lines down",
                          description="Cell towers and phone lines are out of service", lon=15.881111, lat=48.457222,
                          user_id=23)
        report24 = Report(title="Sandbag wall breached", description="Sandbag barriers breached by rising waters",
                          lon=15.955833, lat=48.463611, user_id=24)
        report25 = Report(title="Town square flooded", description="Water levels at the town square are waist-high",
                          lon=16.0125, lat=48.47, user_id=25)
        report26 = Report(title="Sewage contamination",
                          description="Floodwaters are mixed with sewage, causing health risks", lon=15.823333,
                          lat=48.396111, user_id=26)
        report27 = Report(title="Trapped commuters", description="Commuters trapped in buses on the main highway",
                          lon=15.995278, lat=48.1225, user_id=27)
        report28 = Report(title="Volunteers needed", description="More volunteers needed for distribution of supplies",
                          lon=15.735278, lat=48.338611, user_id=28)
        report29 = Report(title="Overflowing riverbanks",
                          description="Riverbanks have overflowed, submerging nearby roads", lon=15.926667,
                          lat=48.212778, user_id=29)
        report30 = Report(title="Displaced families", description="Many families displaced and seeking shelter",
                          lon=15.849444, lat=48.227222, user_id=30)
        report31 = Report(title="Mudslides reported", description="Mudslides occurring due to excessive rain",
                          lon=15.787778, lat=48.395, user_id=31)
        report32 = Report(title="Airport closed", description="Flooding at the airport has forced its closure",
                          lon=16.014722, lat=48.444167, user_id=32)
        report33 = Report(title="School building damaged",
                          description="A school building collapsed, no casualties reported", lon=15.899167,
                          lat=48.204722, user_id=33)
        report34 = Report(title="Floods affecting wildlife", description="Local wildlife displaced by the flooding",
                          lon=15.7625, lat=48.371944, user_id=34)
        report35 = Report(title="Water treatment plant offline",
                          description="Flooding has shut down the water treatment plant", lon=15.858333, lat=48.118611,
                          user_id=35)
        report36 = Report(title="Stagnant water concerns", description="Stagnant water causing mosquito infestations",
                          lon=16.071944, lat=48.145833, user_id=36)
        report37 = Report(title="Railway station underwater",
                          description="Railway station submerged, disrupting travel", lon=15.984167, lat=48.158333,
                          user_id=37)
        report38 = Report(title="River current stronger", description="River current much stronger than expected",
                          lon=15.892778, lat=48.230278, user_id=38)
        report39 = Report(title="Supplies air-dropped", description="Relief supplies air-dropped to inaccessible areas",
                          lon=15.768889, lat=48.417778, user_id=39)
        report40 = Report(title="Flood barriers holding up",
                          description="Flood barriers holding for now, but concerns remain", lon=15.751667,
                          lat=48.443333, user_id=40)

        # List containing all reports
        reports = [
            report1, report2, report3, report4, report5, report6, report7, report8, report9, report10,
            report11, report12, report13, report14, report15, report16, report17, report18, report19, report20,
            report21, report22, report23, report24, report25, report26, report27, report28, report29, report30,
            report31, report32, report33, report34, report35, report36, report37, report38, report39, report40
        ]

        Report.objects.bulk_create(reports)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully inserted {len(reports)} data points')
            )