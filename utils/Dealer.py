import random


def dealer(DEAL_NUMBER):
        """发牌器"""
        list1 = [i + 1 for i in range(10)]
        list2 = []  # 新牌堆开始时为空
        for i in range(DEAL_NUMBER):
            x = random.choice(list1)
            list2.append(x)  # 从原牌堆中随机抽取一张牌放到新牌堆中
            list1.remove(list2[i])  # 从原牌堆中删除刚才抽到的那张牌
        list2.sort()
        return list2
