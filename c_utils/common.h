#ifndef common_h
#define common_h

#include <stdio.h>

unsigned char* read_sk(const char* fname);
unsigned char* read_pk(const char* fname);

int		ParseHex(char *inbuf, unsigned char *A, int Length);
void	fprintBstr(FILE *fp, char *S, unsigned char *A, unsigned long long L);

void fprintMat(FILE *fp, const char* name, unsigned char **M, int nrows, int ncols);

#endif
