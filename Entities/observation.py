class observation:
    def __init__(self,obsv_id,linkU=False,
                 pDrop=False,pLevel=None):
        self.observation_id = obsv_id
        self.link_utilization = linkU
        self.drop_ratio = pDrop
        self.link_Or_drop_level = pLevel

    def print_properties(self):
        print("Observation ID %s"%(self.observation_id))
        if self.link_utilization:
            print('\t Link Utilization Label %s'%(self.link_utilization))
        if self.drop_ratio:
            print('\t Packet Drop Ratio %s'%(self.drop_ratio))
        print('Link Utilization or Packet Drop Ratio %s'%(self.link_Or_drop_level))
