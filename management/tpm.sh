#!/bin/bash

persistent_handle=0x81010021

# primary key
tpm2_createprimary -Q -C o -g sha256 -G rsa -c o.ctx

# create and load asymmetric key
tpm2_create -Q -C o.ctx -g sha256 -G rsa -u myasymmetrickey.pub -r myasymmetrickey.priv
tpm2_load -Q -C o.ctx -u myasymmetrickey.pub -r myasymmetrickey.priv -c myasymmetrickey.ctx

# add key to TPM if not exists
if ! tpm2_getcap handles-persistent | grep -q $persistent_handle; then
    tpm2_evictcontrol -Q -C o -c myasymmetrickey.ctx $persistent_handle
fi

# get random uuid as the secret
uuid=$(cat /proc/sys/kernel/random/uuid)
echo -n $uuid > secret

# encrypt the secret
tpm2_rsaencrypt -Q -c $persistent_handle -o secret.enc2 secret

# save uuid into the database
sqlite3 ../data/data-dev.sqlite "INSERT INTO uids (uid) VALUES ('$uuid');"

echo "You can now transfer the secret.enc2 file to Pico"