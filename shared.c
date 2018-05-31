#include <sys/shm.h> 
#include <sys/stat.h> 
#include <stdio.h> 
#include <stdlib.h>
int main (int argc, char* argv[]) {   
	int seg_id;
	double *data; 
	
	seg_id = shmget(IPC_PRIVATE, sizeof(data), IPC_CREAT | 0666);

	if(seg_id == -1)
	{
		printf("Shared memory creation field \n");
		exit(1);
	}
	else 
	{
		printf("Segment ID is %d \n", seg_id);	
	}
	data = shmat (seg_id, NULL, 0);
	if (data == (double *) -1) 
	{    
		printf ("Fail to attach");    
		exit (1); 
	}
	*data = 713.48;
	shmdt (data); 
	//shmctl (seg_id, IPC_RMID, 0); 
 	return 0; 



}
