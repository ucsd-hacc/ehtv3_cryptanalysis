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
#include "common.h"

#define KAT_SUCCESS          0
#define KAT_FILE_OPEN_ERROR -1
#define KAT_DATA_ERROR      -3
#define KAT_CRYPTO_FAILURE  -4

char    AlgName[] = "ehtv3l1";

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

    if (argc < 4) {
      fprintf(stderr, "Usage: ./eht_siggen secret_key.sk NUMSIGS MSGSEED\n");
      return -1;
    }

    sscanf(argv[2], "%u", &numsigs);
    sscanf(argv[3], "%u", &msgseed);

    // Read the secret key from the file.
    if ((sk = read_sk(argv[1])) == NULL) {
        fprintf(stderr, "Couldn't open <%s> for private key read\n", argv[1]);
        return KAT_FILE_OPEN_ERROR;
    }

    // Generate many signatures over random messages. Output to stdout.
    mlen = 33;
    for (unsigned int i = 0; i < numsigs; i++) {
      // The call to crypto_sign overwrites the PRNG state to something that
      // depends only on sk, so reseed the PRNG to a unique starting value.
      // Randomly generate a message of length MLEN
      ((unsigned int*)entropy_input)[0] = msgseed;
      for (unsigned int j = 1; j < sizeof(entropy_input) / sizeof(unsigned int); j++) {
	((unsigned int*)entropy_input)[j] = i;
      }
      randombytes_init(entropy_input, NULL, 256);
      randombytes(msg, mlen);

      // Get a signature
      sm = (unsigned char *)calloc(mlen+CRYPTO_BYTES, sizeof(unsigned char));
      if ( (ret_val = crypto_sign(sm, &smlen, msg, mlen, sk)) != 0) {
	fprintf(stderr, "crypto_sign returned <%d>\n", ret_val);
	return KAT_CRYPTO_FAILURE;
      }

      // Save it. The signature bytes also contain the message that was signed.
      fprintBstr(stdout, "", sm, smlen);
    
      free(sm);
    }

    fprintf(stderr, "Generated %u signatures.\n", numsigs);

    free(sk);

    return KAT_SUCCESS;
}
