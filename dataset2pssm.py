import os
import traceback
import argparse
import time

# Settings
pssm_folder = os.path.join(os.getcwd(),"pssm","{}")
dataset_folder=os.path.join(os.getcwd(),"dataset","trainTest","{}")
db=pssm_folder.format(os.path.join("db","swissprot.00"))
command="psiblast -query {} -db {} -evalue 1e-3 -matrix BLOSUM62 -num_iterations {} -out_ascii_pssm {} -out {}"

def file2pssm(dataset_files,pssm_iteration):
    
    _temp=pssm_folder.format("temp.fasta")
    
    for file in dataset_files:
        # Reading file content
        file_handler=open(dataset_folder.format(file+".fasta"),"r")
        data=file_handler.read().split(os.linesep)
        file_handler.close()

        #Creating the folder
        _folder = os.path.join("pssm"+str(pssm_iteration),str(len(dataset_files)),file)
        _destination=pssm_folder.format(_folder)
        os.makedirs(_destination, mode=0o777, exist_ok=True)
        
        for _index in range(0,len(data),2):
            _p_name=data[_index][1:]
            _p_seq=data[_index+1]

            print("PSSM >> {}".format(_p_name))
            open(_temp,"w").close()
            handler=open(_temp,"w")
            handler.write(_p_seq)
            handler.close()

            os.system(
                command.format(
                    _temp,db,pssm_iteration,os.path.join(_destination,_p_name),os.path.join(_destination,"out."+_p_name)))    
            
            _handler=open(os.path.join(_destination,_p_name),'a')
            _handler.write("\n"+str(len(_p_seq)))
            _handler.close

            os.remove(os.path.join(_destination,"out."+_p_name))

            


        

def main():
    try:
        # Checking for right argument from user
        parser = argparse.ArgumentParser(
            description='Converting Dataset to PSSM')
        parser.add_argument('_num_of_classes', type=int, help='7 or 8 classes')
        parser.add_argument(
            '_num_of_iterations', type=int, help='2 or 3 iterations')
        parser.parse_args()

        # Logging start of Program
        _num_of_classes = parser.parse_args()._num_of_classes
        _num_of_iterations = parser.parse_args()._num_of_iterations

        nonTransporters=[]
        trasnporters=[]
        for file in os.listdir(dataset_folder.format("")):
            if "nonTransporter" in file:
                nonTransporters.append(file.split(".")[0])
            else:
                if "fasta" in file:
                    trasnporters.append(file.split(".")[0])

        # ???????
        if _num_of_classes==7:
            file2pssm(trasnporters,_num_of_iterations)
        else:
            file2pssm(trasnporters+nonTransporters,_num_of_iterations)



    except Exception:
        print(traceback.format_exc())


if __name__ == "__main__":
    main()