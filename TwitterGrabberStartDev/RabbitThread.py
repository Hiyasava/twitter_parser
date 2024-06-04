from WriteToRabbit import WriteToRabbit
import multiprocessing


class RabbitThread():

    def __init__(self) -> None:
        self.process = multiprocessing.Process()

    def start_process(self,q):
            RabbitProcces = multiprocessing.Process(target=WriteToRabbit, args=(q,), name="RabbitProcess", daemon=True)
            RabbitProcces.start()



         
    
        


        