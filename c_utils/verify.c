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
char    AlgName[] = "ehtv3l1";

int
main(int argc, char** argv)
{
    FILE                *fp_pk;
    unsigned char       seed[48];
    unsigned char       msg[3300];
    unsigned char       entropy_input[48];
    //unsigned char       pk[CRYPTO_PUBLICKEYBYTES];
    int                 ret_val;
    unsigned char* pk;

    if (argc < 2) {
      fprintf(stderr, "Usage: ./sigparse FILE.pk\n");
      return -1;
    }

    // Read the public key from the file.
    if ((pk = read_pk(argv[1])) == NULL) {
        fprintf(stderr, "Couldn't open <%s> for public key read\n", argv[1]);
        return KAT_FILE_OPEN_ERROR;
    }

    // Read the entire stdin into a buffer
    unsigned char* sm= NULL;
    unsigned long long smlen = 0;
    unsigned long long batch_len = 10;

    sm = realloc(sm, smlen + batch_len);

    size_t sz;
    while ((sz = fread(sm+smlen, 1, batch_len, stdin)) != 0) {
      smlen += sz;
      sm = realloc(sm, smlen + batch_len);
    }
    
    unsigned char* m = (unsigned char *)calloc(smlen, sizeof(unsigned char));
    unsigned long long mlen;
    if ( (ret_val = crypto_sign_open(m, &mlen, sm, smlen, pk)) != 0) {
      fprintf(stderr, "Verification failed.\n");
      return -1;
    } else {
      fprintf(stderr, "Verification succeeds.\n");
      return 0;
    }
}
