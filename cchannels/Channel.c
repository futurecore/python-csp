#include "Channel.h"

#define false 0
#define true (!false)
#define SHMSZ     1024
#define printf(x...) ;

int semflg = IPC_CREAT | 0666 | IPC_EXCL; 
int nsems = 1; 
int sq(int i ){
	return i*i;
}

Channel getChannel(long int p,long int av,long int tak,long int shm){
	Channel c;
	int pshared = 0;
	int OldPrio = 0;

	pthread_mutexattr_t mutexattr;
	pthread_mutexattr_settype(&mutexattr, 0);
	pthread_mutexattr_init(&mutexattr);
	

	pthread_mutex_init(&c.r_lock, &mutexattr);
	pthread_mutex_init(&c.w_lock, &mutexattr);
	//printf("%d\n", pthread_mutex_init(&c.r_lock, &mutexattr));
	//printf("%d\n", pthread_mutex_init(&c.w_lock, &mutexattr));
	pthread_mutex_setprioceiling(&c.r_lock, 0, &OldPrio);
	pthread_mutex_setprioceiling(&c.w_lock, 0, &OldPrio);
	
	key_t p_lock_key = p; // GENERATE UUID
	c.p_lock = semget(p_lock_key, nsems, semflg);
	key_t available_key = av; //GENERATE UUID
	c.available = semget(available_key, nsems, semflg);
	key_t taken_key = tak; //GENERATE UUID
	c.taken = semget(taken_key, nsems, semflg);

	union semun ss;

	ss.val = 0;
	//printf("SEMVALUE: %d\n",semctl(c.taken, 0,GETVAL));
	semctl(c.taken, 0,SETVAL,ss);
	semctl(c.p_lock, 0,SETVAL,ss);
	semctl(c.available, 0,SETVAL,ss);
	
	//printf("SEMVALUE: %d\n",semctl(c.taken, 0,GETVAL));

	printf("p_lock: %d available: %d taken: %d\n", c.p_lock,c.available,c.taken);
	c.is_alting = 0;
	c.is_selectable = 0;
	c.has_selected = 0;
	c.poisoned = 0;
	c.sh_mem_name = shm; //GENERATE UUID
	c.shmid = shmget(c.sh_mem_name, SHMSZ, IPC_CREAT | 0666);
	
	
	return c;

}

void removeChannel(Channel *c){
	fprintf(stdout,"RUNNING CHANNEL CLEANUP: ");
	pthread_mutex_destroy(&(*c).r_lock);
	pthread_mutex_destroy(&(*c).w_lock);

	semctl((*c).p_lock, 0, IPC_RMID);
	semctl((*c).available, 0, IPC_RMID);
	semctl((*c).taken, 0, IPC_RMID);
	shmctl((*c).shmid, IPC_RMID,NULL);
	free(c);
}

void semWait(int semid){
	printf("SEMWAIT\n");
	struct sembuf *sops = (struct sembuf *) malloc(2*sizeof(struct sembuf)); 
	//semid = semget(semid, nsems, 0);

	int nsops = 1;
       
       			/* wait for semaphore to reach zero */
       
       	//sops[0].sem_num = 0; /* We only use one track */
      	//sops[0].sem_op = 0; /* wait for semaphore flag to become zero */
       	//sops[0].sem_flg = SEM_UNDO; /* take off semaphore asynchronous  */
       
       
       	sops[0].sem_num = 0;
       	sops[0].sem_op = -1; /* increment semaphore -- take control of track */
       	//sops[0].sem_flg = SEM_UNDO; /* take off semaphore */
       
      
	semop(semid, sops, nsops);
				
		
      	
}

int semTryWait(int semid){
	struct sembuf *sops = (struct sembuf *) malloc(1*sizeof(struct sembuf)); 
	//semid = semget(semid, nsems, 0);
	printf("try wait\n");
	int nsops = 1;
       
       			/* wait for semaphore to reach zero */
       
       	//sops[0].sem_num = 0; /* We only use one track */
      	//sops[0].sem_op = 0; /* wait for semaphore flag to become zero */
       	//sops[0].sem_flg = SEM_UNDO; /* take off semaphore asynchronous  */
       
       
       	sops[0].sem_num = 0;
       	sops[0].sem_op = -1; /* increment semaphore -- take control of track */
       	sops[0].sem_flg =  IPC_NOWAIT; /* take off semaphore */
       
        int err;
	if ((err = semop(semid, sops, nsops)) == -1) {
					
					if(errno == 11){
					printf("Could not acquire semaphore RETURNING 0\n");
					return 0;
					}
					perror("semop: semop failed:");
					printf("ERROR CODE: %d\n",errno);
					return 0;
		} 
	printf("return from semop: %d\n", err);
	return 1;
				
		
      	
}

void semPost(int semid){
	printf("SEMPOST\n");
	struct sembuf *sops = (struct sembuf *) malloc(2*sizeof(struct sembuf)); 
	//semid = semget(semid, nsems, 0);

	int nsops = 1;
       
       	/* wait for semaphore to reach zero */
       	sops[0].sem_num = 0;
        sops[0].sem_op = 1; /* Give UP COntrol of track */
       	sops[0].sem_flg =  IPC_NOWAIT; /* take off semaphore, asynchronous  */

	semop(semid, sops, nsops);
}

void getStatus(Channel *c){
	int rlock;
	int wlock;
	int plock  = semctl((*c).p_lock, 0,GETVAL);
	int available = semctl((*c).available, 0,GETVAL);
	int taken = semctl((*c).taken, 0,GETVAL); 
	//sem_getvalue(&(*c).p_lock, &plock); 
	//sem_getvalue(&(*c).available, &available); 
	//sem_getvalue(&(*c).taken, &taken); 
	printf(" r_lock:  w_lock:  p_lock: %d available: %d taken: %d is_alting: %d is_selectable: %d has_selected: %d poisoned: %d\n Item: %s\n", plock, available, taken, (*c).is_alting, (*c).is_selectable, (*c).has_selected,(*c).poisoned, (*c).item);
}

void checkpoison(Channel *c){

	semWait((*c).p_lock);
	if((*c).poisoned){
		printf("%s\n", "This channel has been poisoned");
	}
	semPost((*c).p_lock);
	return;
}

void put(Channel *c, char *ptr, int len){
	(*c).len =len;
	int i = 0;	
	printf("Pickle str: %s\n", ptr);
	char* s = shmat((*c).shmid, NULL, 0);
	//char* start_address = (*c).item;
	for(;i<len; i++){
		*s = *ptr;
		ptr++;
		s++;
	}
	//(*c).item = start_address;
	printf("FINISHED PUT CHAR Length: %d\n",len);
}

char *get(Channel *c){
	char* s = shmat((*c).shmid, NULL, 0);
	int count = 0;
	while(*s != '.'){
		count++;
		s++;
	}
	s = s-count;
	count++;

	
	char* ret = (char*)malloc(count * sizeof (char*));

	int i = 0;
	//char* start_address = (*c).item;
	
	
	printf("ABOUT TO GET: %s   :  %d\n",s,count); 
	
	ret = strdup(s);

	//ptr = ptr-(count-1);
	//ptr = ret;

	printf("Have got: %s\n",ret); 
	return ret;
	//(*c).item = start_address;
}

int is_selectable(Channel *c){
	//checkpoison(c);
	printf("%s\n"," c is_selectable called");
	return (*c).is_selectable;
}

void _write(Channel *c, char *ptr, int len){
	//checkpoison(c);
	printf("%s\n", "+++ WRITE ON CHANNEL STARTED +++");
	pthread_mutex_lock(&(*c).w_lock);
	printf("%s\n", "+++ ACQUIRED w_lock +++");
	(*c).has_selected = false;

	// ########## DO PUT ###########
	put(c,ptr, len);
	printf("%s\n", "+++ STORED ITEM +++");
	printf("+++ ABOUT TO POST TO : %d +++\n",(*c).available);
	semPost((*c).available);
	printf("%s\n", "+++ RELEASED AVAILABLE +++");
	getStatus(c);
	semWait((*c).taken);
	printf("%s\n", "+++ ACQUIRED TAKEN +++");
	pthread_mutex_unlock(&(*c).w_lock);
	printf("%s\n", "+++ WRITE ON CHANNEL FINISHED+++");
}



char *_read(Channel *c){
	//checkpoison(c);
	printf("%s\n", "+++ READ ON CHANNEL STARTED +++");
	pthread_mutex_lock(&(*c).r_lock);
	printf("%s\n", "+++ ACQUIRED r_lock +++");
	getStatus(c);
	printf("%s\n", "+++ WAITING TO ACQUIRE AVAILABLE +++");
	getStatus(c);
	semWait((*c).available);
	printf("%s\n", "+++ ACQUIRED AVAILABLE +++");
	getStatus(c);
	// ########## DO GET ##############
	char *retval;
	printf("BEFORE: %s\n",retval);
	retval = get(c);
	printf("AFTER: %s\n",retval);
	printf("%s\n", "+++ RETRIEVED ITEM +++");
	semPost((*c).taken);
	getStatus(c);
	printf("%s\n", "+++ RELEASED TAKEN +++");
	pthread_mutex_unlock(&(*c).r_lock);	
	printf("%s\n", "+++ READ ON CHANNEL FINISHED+++");
	printf("WHAT READ RETURNED: %s\n",retval);
	return retval;	
}

void enable(Channel *c){
	
	//checkpoison(c);
	printf("%s\n", "++++ ABOUT TO CHECKED has_selected || is_selectabled +++++");
	if((*c).has_selected || is_selectable(c)){
		return;
	} 
	(*c).is_alting = true;
	printf("%s\n", "++++ ABOUT TO GET r_lock+++++");
	pthread_mutex_lock(&(*c).r_lock);
	printf("%s\n", "++++ GOT  r_lock+++++");
	
	if(semTryWait((*c).available)){
		(*c).is_selectable = true;
	} else {
		(*c).is_selectable = false;
	}
	printf("%s %d\n", "++++ is_selectable ++++", (*c).is_selectable);
	pthread_mutex_unlock(&(*c).r_lock);
	printf("%s\n", "+++++ RELEASED r_lock ++++++");
	return;

}

void disable(Channel *c){
	//checkpoison(c);
	(*c).is_alting = false;
	if((*c).is_selectable == true){
		pthread_mutex_lock(&(*c).r_lock);
		semPost((*c).available);
		pthread_mutex_unlock(&(*c).r_lock);
		(*c).is_selectable = false;
	}
	return;

}

char *_select(Channel *c){
	//checkpoison(c);
		
	// ASSERT STATEMENT?

	pthread_mutex_lock(&(*c).r_lock);
		printf("%s\n", "GOT READ LOCK ON CHANNEL");
		char *retval = get(c);
		printf("%s\n", "GOT OBJECT");
		semPost((*c).taken);
		printf("%s\n", "RELEASE TAKEN");
		(*c).is_selectable = false;
		(*c).is_alting = false;
		(*c).has_selected = true;
	pthread_mutex_unlock(&(*c).r_lock);
	return retval;
}

void poison(Channel *c){
	sem_wait((*c).p_lock);
		(*c).poisoned = true;
		
		sem_post((*c).available);
		sem_post((*c).taken);
	sem_post((*c).p_lock);
	return;	
}


