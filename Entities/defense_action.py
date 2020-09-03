import global_settings

class defense:
    def __init__(self,defense_id,limit_ratio=None,limit_type=None):
        self.defense_id = defense_id
        self.limit_ratio = limit_ratio
        self.limit_type = limit_type
        if limit_ratio is None:
            self.diversion_ratio = -1
            self.limit_type = -1
        else:
            self.diversion_ratio = 1-limit_ratio
        self.limited_traffic_amount = 0
        self.diverted_traffic_amount = 0
        self.chosen_limit_vector_ratio = None
        self.traffic_drop_start_point = None

    def __choose_limit_function(self):
        # print("Traffic to be limited %s"%(self.limited_traffic_amount))
        traffic_to_be_limited = self.limited_traffic_amount
        sp,li = 1,100
        min_error = None
        while sp <= li:
            si = (sp+li)//2
            delta_space = 100/si
            l_t = 0
            limit_ratio_vector = []
            for i in range(si):
                limit_ratio_vector.append(0.0)

            d_t = si
            for i in range(si,101):
                limit_ratio_vector.append((global_settings.convex_n*d_t)**global_settings.convex_v)
                d_t += delta_space
            global_settings.normalize_vector_by_max(limit_ratio_vector)
            for i in range(1,101):
                l_t += global_settings.traffic_dist_risk_scores[i]*limit_ratio_vector[i]
            # print("Limit Ratio with n==%s and v==%s -->\n %s" % (
            # global_settings.convex_n, global_settings.convex_v, limit_ratio_vector))
            # print('Limited Traffic %s from %s' % (l_t,si))

            if abs((traffic_to_be_limited-l_t)/traffic_to_be_limited) <= global_settings.affordable_volume_error_threshold:
                self.chosen_limit_vector_ratio = limit_ratio_vector
                self.limited_traffic_amount = l_t
                self.traffic_drop_start_point = si
                break
            elif (traffic_to_be_limited-l_t)/traffic_to_be_limited > global_settings.affordable_volume_error_threshold:
                li = si - 1
            else:
                sp = si+1
            if min_error is None or abs((traffic_to_be_limited-l_t)/traffic_to_be_limited) < min_error:
                self.chosen_limit_vector_ratio = limit_ratio_vector
                # print('%s < %s'%(abs((traffic_to_be_limited-l_t)/traffic_to_be_limited),min_error))
                min_error = abs((traffic_to_be_limited-l_t)/traffic_to_be_limited)
                self.limited_traffic_amount = l_t
                self.traffic_drop_start_point = si

            # print()

    def __choose_limit_function_concave(self):
        # print("Traffic to be limited with Concave Function %s"%(self.limited_traffic_amount))
        traffic_to_be_limited = self.limited_traffic_amount
        sp,li = 1,100
        min_error = None
        while sp <= li:
            si = (sp+li)//2
            delta_space = 100/si
            l_t = 0
            limit_ratio_vector = []
            for i in range(si):
                limit_ratio_vector.append(0.0)
            d_t = si
            for i in range(si,101):
                limit_ratio_vector.append((global_settings.concave_n*d_t)**global_settings.concave_v)
                d_t += delta_space

            global_settings.normalize_vector_by_max(limit_ratio_vector)
            for i in range(1,101):
                l_t += global_settings.traffic_dist_risk_scores[i]*limit_ratio_vector[i]
            # print("Limit Ratio with n==%s and v==%s -->\n %s" % (
            # global_settings.convex_n, global_settings.convex_v, limit_ratio_vector))
            # print('Limited Traffic %s from %s' % (l_t,si))

            if abs((traffic_to_be_limited-l_t)/traffic_to_be_limited) <= global_settings.affordable_volume_error_threshold:
                self.chosen_limit_vector_ratio = limit_ratio_vector
                self.limited_traffic_amount = l_t
                self.traffic_drop_start_point = si
                break
            elif (traffic_to_be_limited-l_t)/traffic_to_be_limited > global_settings.affordable_volume_error_threshold:
                li = si - 1
            else:
                sp = si+1
            if min_error is None or abs((traffic_to_be_limited-l_t)/traffic_to_be_limited) < min_error:
                self.chosen_limit_vector_ratio = limit_ratio_vector
                # print('%s < %s'%(abs((traffic_to_be_limited-l_t)/traffic_to_be_limited),min_error))
                min_error = abs((traffic_to_be_limited-l_t)/traffic_to_be_limited)
                self.limited_traffic_amount = l_t
                self.traffic_drop_start_point = si

        # print(self.traffic_drop_start_point)

    def ____choose_limit_function_traditional(self):
        # print("Traffic to be limited with Taditional Blocking %s"%(self.limited_traffic_amount))
        traffic_to_be_limited = self.limited_traffic_amount
        sp, li = 1, 100
        min_error = None
        while sp <= li:
            si = (sp+li)//2
            l_t = 0
            for i in range(si,101):
                l_t += global_settings.traffic_dist_risk_scores[i]

            # print('Limited Traffic %s from %s' % (l_t, si))
            if abs((traffic_to_be_limited-l_t)/traffic_to_be_limited) <= global_settings.affordable_volume_error_threshold:
                self.chosen_limit_vector_ratio = [1.0 if si >= k else 0.0 for k in range(101)]
                self.limited_traffic_amount = l_t
                self.traffic_drop_start_point = si
                break
            elif (traffic_to_be_limited-l_t)/traffic_to_be_limited > global_settings.affordable_volume_error_threshold:
                li = si - 1
            else:
                sp = si+1
            if min_error is None or abs((traffic_to_be_limited-l_t)/traffic_to_be_limited) < min_error:
                self.chosen_limit_vector_ratio = [1.0 if k >= si else 0.0 for k in range(101)]
                # print('%s < %s'%(abs((traffic_to_be_limited-l_t)/traffic_to_be_limited),min_error))
                min_error = abs((traffic_to_be_limited-l_t)/traffic_to_be_limited)
                self.limited_traffic_amount = l_t
                self.traffic_drop_start_point = si

    def set_limited_traffic_amount(self,congested_traffic_amount):
        self.limited_traffic_amount = self.limit_ratio*congested_traffic_amount
        self.diverted_traffic_amount = congested_traffic_amount - self.limited_traffic_amount
        if self.limit_type ==0 and global_settings.convex_limit_function_type==0:
            self.__choose_limit_function()
        if self.limit_type==1 and global_settings.concave_limit_function_type==0:
            self.__choose_limit_function_concave()
        if self.limit_type==2:
            self.____choose_limit_function_traditional()
        if self.limited_traffic_amount > self.limit_ratio*congested_traffic_amount:
            d_ratio = (self.limit_ratio*congested_traffic_amount)/self.limited_traffic_amount
            for i in range(100):
                self.chosen_limit_vector_ratio[i] *= d_ratio
            self.limited_traffic_amount *= d_ratio
        # print("Current Traffic Limit Amount %s from %s"%(self.limited_traffic_amount,self.traffic_drop_start_point))
        self.diverted_traffic_amount = congested_traffic_amount - self.limited_traffic_amount

    def print_properties(self):
        print("Defense ID %s"%(self.defense_id))
        print("\t Limit Traffic Ratio %s"%(self.limit_ratio))
        print("\t Limit Function type %s"%(global_settings.limit_function_map[self.limit_type]))
