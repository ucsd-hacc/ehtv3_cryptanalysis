/*
NIST-developed software is provided by NIST as a public service. You may use, copy, and distribute copies of the software in any medium, provided that you keep intact this entire notice. You may improve, modify, and create derivative works of the software or any portion of the software, and you may copy and distribute such modifications or works. Modified works should carry a notice stating that you changed the software and should note the date and nature of any such change. Please explicitly acknowledge the National Institute of Standards and Technology as the source of the software.
 
NIST-developed software is expressly provided "AS IS." NIST MAKES NO WARRANTY OF ANY KIND, EXPRESS, IMPLIED, IN FACT, OR ARISING BY OPERATION OF LAW, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, AND DATA ACCURACY. NIST NEITHER REPRESENTS NOR WARRANTS THAT THE OPERATION OF THE SOFTWARE WILL BE UNINTERRUPTED OR ERROR-FREE, OR THAT ANY DEFECTS WILL BE CORRECTED. NIST DOES NOT WARRANT OR MAKE ANY REPRESENTATIONS REGARDING THE USE OF THE SOFTWARE OR THE RESULTS THEREOF, INCLUDING BUT NOT LIMITED TO THE CORRECTNESS, ACCURACY, RELIABILITY, OR USEFULNESS OF THE SOFTWARE.
 
You are solely responsible for determining the appropriateness of using and distributing the software and you assume all risks associated with its use, including but not limited to the risks and costs of program errors, compliance with applicable laws, damage to or loss of data, programs or equipment, and the unavailability or interruption of operation. This software is not intended to be used in any situation where a failure could cause risk of injury or damage to property. The software developed by NIST employees is not subject to copyright protection within the United States.

Modified July 2023 by Keegan Ryan.

*/

#include "common.h"

#include "api.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>

unsigned char* read_sk(const char* fname) {
  FILE *fp_sk;
  if ( (fp_sk = fopen(fname, "r")) == NULL ) {
    return NULL;
  }

  // Read private key from file
  unsigned char* sk = (unsigned char *)calloc(CRYPTO_SECRETKEYBYTES, sizeof(unsigned char));
  size_t len = fread(sk, sizeof(unsigned char), CRYPTO_SECRETKEYBYTES, fp_sk);
  if (len != CRYPTO_SECRETKEYBYTES) {
    free(sk);
    return NULL;
  }
    
  return sk;
}

unsigned char* read_pk(const char* fname) {
  FILE *fp_pk;
  if ( (fp_pk = fopen(fname, "r")) == NULL ) {
    return NULL;
  }

  // Read public key from file
  unsigned char* pk = (unsigned char *)calloc(CRYPTO_PUBLICKEYBYTES, sizeof(unsigned char));
  size_t len = fread(pk, sizeof(unsigned char), CRYPTO_PUBLICKEYBYTES, fp_pk);
  if (len != CRYPTO_PUBLICKEYBYTES) {
    free(pk);
    return NULL;
  }
    
  return pk;
}

void
fprintBstr(FILE *fp, char *S, unsigned char *A, unsigned long long L)
{
	unsigned long long  i;

	fprintf(fp, "%s", S);

	for ( i=0; i<L; i++ )
		fprintf(fp, "%02X", A[i]);

	if ( L == 0 )
		fprintf(fp, "00");

	fprintf(fp, "\n");
}

//
// ALLOW TO READ HEXADECIMAL ENTRY (KEYS, DATA, TEXT, etc.)
//
int
ParseHex(char *inbuf, unsigned char *A, int Length)
{
	int			i, ch, started;
	unsigned char	ich;

	if ( Length == 0 ) {
		A[0] = 0x00;
		return 1;
	}
	memset(A, 0x00, Length);
	started = 0;
	while ( (ch = *inbuf++) != '\0' ) {
	  if ( !isxdigit(ch) ) {
	    if ( !started ) {
	      if ( ch == '\n' )
		break;
	      else
		continue;
	    }
	    else
	      break;
	  }
	  started = 1;
	  if ( (ch >= '0') && (ch <= '9') )
	    ich = ch - '0';
	  else if ( (ch >= 'A') && (ch <= 'F') )
	    ich = ch - 'A' + 10;
	  else if ( (ch >= 'a') && (ch <= 'f') )
	    ich = ch - 'a' + 10;
	  else // shouldn't ever get here
	    ich = 0;
	  
	    for ( i=0; i<Length-1; i++ )
	      A[i] = (A[i] << 4) | (A[i+1] >> 4);
	    A[Length-1] = (A[Length-1] << 4) | ich;
	}
	return 1;
}

void fprintMat(FILE *fp, const char* name, unsigned char **M, int nrows, int ncols) {
  //fprintf(fp, "%s = [\n", name);
  fprintf(fp, "[\n");
  for (unsigned int i = 0; i < nrows; i++) {
    fprintf(fp, "[");
    for (unsigned int j = 0; j < ncols; j++) {
      fprintf(fp, "%d", M[i][j]);
      if (j < ncols - 1) {
	fprintf(fp, ", ");
      }
    }
    fprintf(fp, (i < nrows - 1) ? "],\n": "]\n");
  }
  fprintf(fp, "]\n");
}
