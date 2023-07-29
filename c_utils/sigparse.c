/*
NIST-developed software is provided by NIST as a public service. You may use, copy, and distribute copies of the software in any medium, provided that you keep intact this entire notice. You may improve, modify, and create derivative works of the software or any portion of the software, and you may copy and distribute such modifications or works. Modified works should carry a notice stating that you changed the software and should note the date and nature of any such change. Please explicitly acknowledge the National Institute of Standards and Technology as the source of the software.
 
NIST-developed software is expressly provided "AS IS." NIST MAKES NO WARRANTY OF ANY KIND, EXPRESS, IMPLIED, IN FACT, OR ARISING BY OPERATION OF LAW, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, AND DATA ACCURACY. NIST NEITHER REPRESENTS NOR WARRANTS THAT THE OPERATION OF THE SOFTWARE WILL BE UNINTERRUPTED OR ERROR-FREE, OR THAT ANY DEFECTS WILL BE CORRECTED. NIST DOES NOT WARRANT OR MAKE ANY REPRESENTATIONS REGARDING THE USE OF THE SOFTWARE OR THE RESULTS THEREOF, INCLUDING BUT NOT LIMITED TO THE CORRECTNESS, ACCURACY, RELIABILITY, OR USEFULNESS OF THE SOFTWARE.
 
You are solely responsible for determining the appropriateness of using and distributing the software and you assume all risks associated with its use, including but not limited to the risks and costs of program errors, compliance with applicable laws, damage to or loss of data, programs or equipment, and the unavailability or interruption of operation. This software is not intended to be used in any situation where a failure could cause risk of injury or damage to property. The software developed by NIST employees is not subject to copyright protection within the United States.

Modified July 2023 by Keegan Ryan.

*/

#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "rng.h"
#include "parameters.h"
#include "general_functions.h"
#include "api.h"

#include "common.h"

#define	MAX_MARKER_LEN		50

#define KAT_SUCCESS          0
#define KAT_FILE_OPEN_ERROR -1
#define KAT_DATA_ERROR      -3
#define KAT_CRYPTO_FAILURE  -4

// Defined in eht_sigver.c
void pk_to_A(const unsigned char *pk, unsigned char **A);
void sm_to_mx(const unsigned char* sm, unsigned long long smlen, unsigned char* m, unsigned long long* mlen, unsigned char** x);
  
char    AlgName[] = "ehtv3l1";

int
main(int argc, char** argv)
{
    FILE                *fp_pk;
    unsigned char       seed[48];
    unsigned char       msg[3300];
    unsigned char       entropy_input[48];
    unsigned char       *m, *sm;
    unsigned long long  mlen, smlen, mlen1;
    //unsigned char       pk[CRYPTO_PUBLICKEYBYTES];
    int                 ret_val;
    unsigned char* pk;

    char *line = NULL;
    size_t len = 0;
    ssize_t nread;
    

    unsigned char** A;
    unsigned char** x;
    unsigned char** Ax;
    unsigned char** h;

    if (argc < 2) {
      fprintf(stderr, "Usage: ./sigparse FILE.pk\n");
      return -1;
    }

    // Read the public key from the file.
    if ((pk = read_pk(argv[1])) == NULL) {
        fprintf(stderr, "Couldn't open <%s> for public key read\n", argv[1]);
        return KAT_FILE_OPEN_ERROR;
    }

    // Allocate memory for matrices
    A = allocate_unsigned_char_matrix_memory(M, N);
    x = allocate_unsigned_char_matrix_memory(N, 1);
    Ax = allocate_unsigned_char_matrix_memory(M, 1);
    // HASH of Message
    h = allocate_unsigned_char_matrix_memory(M, 1);
    
    if(A==NULL || x==NULL || Ax==NULL || h==NULL) {
      fprintf(stderr, "Memory error.\n");
      return KAT_DATA_ERROR;
    }

    pk_to_A(pk, A);
    free(pk);

    int count = 0;

    while ((nread = getline(&line, &len, stdin)) != -1) {
      smlen = (nread - 1) / 2;
      sm = (unsigned char *)calloc(smlen, sizeof(unsigned char));
      ParseHex(line, sm, smlen);

      m = (unsigned char *)calloc(smlen, sizeof(unsigned char));
      /*
      if ( (ret_val = crypto_sign_open(m, &mlen1, sm, smlen, pk)) != 0) {
	// Skip lines that don't validate
	free(sm);
	free(m);
	continue;
	//fprintf(stderr, "crypto_sign_open returned <%d>\n", ret_val);
	//return KAT_CRYPTO_FAILURE;
	}*/

      sm_to_mx(sm, smlen, m, &mlen, x);

      // Get h
      hash_of_message(m, mlen, h);
	
      // Get Ax = A*x
      matrix_multiply(M, N, 1, A, x, Ax); // A*x

      // Get e = h - A*x = Cz
      for (unsigned int i = 0; i < M; i++) {
	unsigned char e = s_mod_q(h[i][0] - Ax[i][0]);
	// Output single byte representing e[i] mod Q
	fwrite(&e, 1, 1, stdout);
      }
      
      free(m);
      free(sm);

      count += 1;
      if (count % 1000 == 0) {
	fprintf(stderr, "%d\n", count);
      }
    }

    free(line);

    // Free h and Ax as we are done
    free_matrix(M, h); h = NULL;
    free_matrix(M, Ax); Ax = NULL;
    // Free A and x
    free_matrix(M, A); A = NULL;
    free_matrix(N, x); x = NULL;

    return 0;
}
