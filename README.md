# Instructions
Run the numbered shell scripts in order:
 * `00_setup.sh` builds the ehtv3 reference implementation and wrapper and extracts a keypair from the KAT
 * `01_signature_generation.sh` generates signatures. (This is the only step that uses the private key.)
 * `02_process_signatures.sh` uses the public key to turn each signature `x_i` into a sample `C z_i mod 47`, where each `z_i` is unknown but has coefficents bounded by +-3.
 * `03_hzp_morphing.sh` runs the first part of the DucasNguyen12 HZP algorithm: it goes from the Cz vectors (whose distribution is roughly (a projection of) the uniform distribution over some parallelepiped) to "morphed" vectors (a projection of the uniform distribution over a hypercube) and the transformation matrix of the morphing.
 * `04_hzp_descent.sh` runs the second part of DucasNguyen12: it performs gradient descent to find minima of a particular funtion that involves the morphed vectors. These minima should be the columns of C (up to sign). This script runs many gradient descents in parallel, then collects and deduplicates the resulting vectors, hopefully recovering all the columns of C.
 * `05_partial_key_recovery` uses the recovered columns of C (which are not in order, may contain false positives, and are only known up to sign) to recover almost all columns of T, C, and B; in particular this partial private key is enough to produce forgeries.
 * `06_signature_forgery.sh` uses the partial private key to forge a signature and checks that the signature verifies.

# Testing
To test the partial key recovery attack without running the HZP algorithm:
 * `00_setup.sh` builds the ehtv3 reference implementation and wrapper and extracts a keypair from the KAT
 * `99_debug.sh` skips the HZP algorithm that is performed in the full attack, and it performs the partial key recovery attack directly on the shuffled columns of C.
