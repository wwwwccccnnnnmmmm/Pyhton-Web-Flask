from datetime import datetime
import random
def generate_order_number():
    '''
    订单编号:目前的年月日时分+三位随机数
    '''
    now_part = datetime.now().strftime("%m%d%H%M%S")
    random_part = str(random.randint(100,999))
    
    return now_part+random_part 
