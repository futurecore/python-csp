/* Channel.i */
 %module Channel
 %{
#include </usr/include/semaphore.h>
#include <stdio.h>
#include "Channel.h"

 extern int sq(int i);
 extern void getStatus(Channel *c);
 extern Channel getChannel(long int p,long int av,long int tak,long int shm);
 extern void removeChannel(Channel *c);
 extern void checkpoison(Channel *c);
 extern void put(Channel *c, char *ptr, int len);
 extern void get(Channel *c, char *ptr);
 extern int is_selectable(Channel *c);
 extern void _write(Channel *c, char *ptr,int len);
 extern char *_read(Channel *c);
 extern void enable(Channel *c);
 extern void disable(Channel *c);
 extern char *_select(Channel *c);
 extern void poison(Channel *c);

 %}


 extern int sq(int i);
 extern void getStatus(Channel *c);
 extern Channel getChannel(long int p,long int av,long int tak,long int shm);
 extern void removeChannel(Channel *c);
 extern void checkpoison(Channel *c);
 extern void put(Channel *c, char *ptr, int len);
 extern void get(Channel *c, char *ptr);
 extern int is_selectable(Channel *c);
 extern void _write(Channel *c, char *ptr,int len);
 extern char *_read(Channel *c);
 extern void enable(Channel *c);
 extern void disable(Channel *c);
 extern char *_select(Channel *c);
 extern void poison(Channel *c);
