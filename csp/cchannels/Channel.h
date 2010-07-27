
#include </usr/include/pthread.h>
 #include <stdio.h>
 #include <sys/types.h>
 #include <sys/ipc.h>
 #include <sys/sem.h>
 #include <stdlib.h>
#include <sys/shm.h> 
#include <string.h>
#include <errno.h>
#define false 0
#define true (!false)

typedef struct{
	pthread_mutex_t r_lock;
	pthread_mutex_t w_lock;
	key_t p_lock_key;
	int p_lock;
	key_t available_key;
	int available;
	key_t taken_key;
	int taken;
	unsigned int is_alting;
	unsigned int is_selectable;
	unsigned int has_selected;
	unsigned int poisoned;
	char* item;
	key_t sh_mem_name;
	//char *shm;
	int shmid;
	int len;

}Channel;

union semun {
    int val;
    struct semid_ds *buf;
    ushort *array;
};
