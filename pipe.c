#include <unistd.h>   
#include <fcntl.h> 
#include <stdio.h> 
#include <string.h>

char *childMessage = "Hello, from child";
char *parentMessage = "Hello, from parent";

void main() 
{
	char buf[1024];
	int fd[2];
	int status = 0;
	pipe(fd);
	if(fork() == 0) 
	{

		/*Child */
	
		read(fd[0], buf, 1024);
	
		printf("Parent Sent %s \n", buf);

		write(fd[1], childMessage, strlen(childMessage) + 1);
		//read(fd[0], buf, 1024);	
		exit(status);
	}	
	else 
	{

		write(fd[1], parentMessage, strlen(parentMessage) + 1);
		/*Parent */
		wait(status);
		read(fd[0], buf, 1024);
		printf("Child sent %s \n", buf);
		
		//write(fd[1], message, strlen(message) + 1);
		

	}


}
