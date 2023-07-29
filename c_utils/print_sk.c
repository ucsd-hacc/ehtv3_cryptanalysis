/*
NIST-developed software is provided by NIST as a public service. You may use, copy, and distribute copies of the software in any medium, provided that you keep intact this entire notice. You may improve, modify, and create derivative works of the software or any portion of the software, and you may copy and distribute such modifications or works. Modified works should carry a notice stating that you changed the software and should note the date and nature of any such change. Please explicitly acknowledge the National Institute of Standards and Technology as the source of the software.
 
NIST-developed software is expressly provided "AS IS." NIST MAKES NO WARRANTY OF ANY KIND, EXPRESS, IMPLIED, IN FACT, OR ARISING BY OPERATION OF LAW, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, AND DATA ACCURACY. NIST NEITHER REPRESENTS NOR WARRANTS THAT THE OPERATION OF THE SOFTWARE WILL BE UNINTERRUPTED OR ERROR-FREE, OR THAT ANY DEFECTS WILL BE CORRECTED. NIST DOES NOT WARRANT OR MAKE ANY REPRESENTATIONS REGARDING THE USE OF THE SOFTWARE OR THE RESULTS THEREOF, INCLUDING BUT NOT LIMITED TO THE CORRECTNESS, ACCURACY, RELIABILITY, OR USEFULNESS OF THE SOFTWARE.
 
You are solely responsible for determining the appropriateness of using and distributing the software and you assume all risks associated with its use, including but not limited to the risks and costs of program errors, compliance with applicable laws, damage to or loss of data, programs or equipment, and the unavailability or interruption of operation. This software is not intended to be used in any situation where a failure could cause risk of injury or damage to property. The software developed by NIST employees is not subject to copyright protection within the United States.

Modified July 2023 by Keegan Ryan.

*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "rng.h"
#include "api.h"
#include "parameters.h"
#include "general_functions.h"

#include "common.h"

#define KAT_SUCCESS          0
#define KAT_FILE_OPEN_ERROR -1
#define KAT_DATA_ERROR      -3
#define KAT_CRYPTO_FAILURE  -4

char    AlgName[] = "ehtv3l1";

// From eht_siggen.c
void generate_C(unsigned char** C, unsigned short** C1_index, unsigned char** C1_value);

int
main(int argc, char** argv)
{
    char                fn_sk[32], fn_pk[32];
    FILE                *fp_sk;
    unsigned char       seed[48];
    unsigned char       msg[3300];
    unsigned char       entropy_input[48];
    unsigned char       *m, *sm, *m1;
    unsigned long long  mlen, smlen, mlen1;
    unsigned char*      sk;
    int                 ret_val;
    unsigned int        numsigs, msgseed;

    if (argc < 2) {
      fprintf(stderr, "Usage: ./eht_siggen secret_key.sk\n");
      return -1;
    }

    // Read the secret key from the file.
    if ((sk = read_sk(argv[1])) == NULL) {
        fprintf(stderr, "Couldn't open <%s> for private key read\n", argv[1]);
        return KAT_FILE_OPEN_ERROR;
    }

    unsigned char** C;
    unsigned short** C1_index;
    unsigned char** C1_value;
    unsigned char** T;
    unsigned char** B, **LM, **UM;

    C = allocate_unsigned_char_matrix_memory(M, M+D);
    C1_index = allocate_unsigned_short_matrix_memory(M, NORM1);
    C1_value = allocate_unsigned_char_matrix_memory(M, NORM1);
    
    if(C==NULL || C1_index==NULL || C1_value==NULL) {
      fprintf(stderr, "Could not allocate C\n");
      return -1;
    }

    T = allocate_unsigned_char_matrix_memory(K*N, N);
    if (T==NULL) {
      fprintf(stderr, "Could not allocate T\n");
      return -1;
    }

    // Matrix B Generation from LM and UM (lower and upper triangular matrix construction)
    B = allocate_unsigned_char_matrix_memory(N, N);
    LM = allocate_unsigned_char_matrix_memory(N, N);
    UM = allocate_unsigned_char_matrix_memory(N, N);
	
    if(B==NULL || LM==NULL || UM==NULL) {
      fprintf(stderr, "Could not allocate B\n");
      return -1;
    }
	
    // Initialize the rng
    randombytes_init((unsigned char*)sk, NULL, 256);
    
    generate_C(C, C1_index, C1_value);

    // Initialize T to all zeros.
    zero_matrix(K*N, N, T);
	
    for(int i=0; i<K*N; i++)
      {
        // Fill in the lower triangular part of T with random numbers.
	for(int j=0; j<i/2; j++)
	  {
	    T[i][j] = NIST_rng(Q);
	  }
		
        // The diagonal of T contains tuples.
	T[i][i/2] = TUPPLE[i%K];
      }
	
    zero_matrix(N, N, LM);
    
    for(int i=0; i<N; i++)
      {
	LM[i][i] = 1 + NIST_rng(Q-1);
	
	for(int j=i+1; j<N; j++)
	  {
	    LM[j][i] = NIST_rng(Q);
	  }
      }
    
    zero_matrix(N, N, UM);
    
    for(int i=0; i<N; i++)
      {
	UM[i][i] = 1 + NIST_rng(Q-1);
	
	for(int j=0; j<i; j++)
	  {
	    UM[j][i] = NIST_rng(Q);
	  }
      }
    
    // Compute B = LM*UM
    matrix_multiply(N, N, N, LM, UM, B); 
	
    // We no longer need the matrices LM and UM.
    free_matrix(N, LM); LM = NULL;
    free_matrix(N, UM); UM = NULL;

    printf("{\n");
    printf("\t\"C\": ");
    fprintMat(stdout, "C", C, M, M+D);
    printf(",\n");

    printf("\t\"T\": ");
    fprintMat(stdout, "T", T, K*N, N);
    printf(",\n");
    
    printf("\t\"B\": ");
    fprintMat(stdout, "B", B, N, N);
    printf("}\n");

    free(sk);

    return KAT_SUCCESS;
}
