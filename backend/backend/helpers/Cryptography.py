import pathlib
from typing import Tuple
from uuid import uuid4

from django.conf import settings
from django.core.cache import cache

from backend.helpers.Process import Process
from backend.helpers.Log import Log


class Cryptography:
    @staticmethod
    def generateSshKeys() -> Tuple[str, str]:
        outFile = ""
        private = public = ""

        try:
            outFile = "/tmp/" + str(uuid4())

            success, status, output = Process.execute("ssh-keygen -t ecdsa -N '' -q -f " + outFile)
            if success:
                with open(outFile) as fpr:
                    private = fpr.read()
                with open(outFile + ".pub") as fpu:
                    public = fpu.read()

            return public.strip(), private.strip()
        except Exception as e:
            raise e
        finally:
            if outFile:
                pathlib.Path(outFile).unlink()
                pathlib.Path(outFile + ".pub").unlink()



    @staticmethod
    def getPublicSshKey() -> str:
        try:
            with open("/var/www/.ssh/id_ecdsa.pub") as f:
                return f.read().strip("\n")
        except Exception as e:
            raise e



    @staticmethod
    def addKnownHost(address: str, pubkey: str) -> None:
        knownHostsFile = "/var/www/.ssh/known_hosts"
        doUpdate = True
        knownHosts = ""

        try:
            if not cache.get("knownHosts.lock"): # naive concurrency.
                cache.set("knownHosts.lock", True, timeout=settings.LOCK_MAX_VALIDITY)

                try:
                    # Try opening the file in w mode as little as possible.
                    # First read, and do not proceed further if the updated pubkey is already associated to the address.
                    with open(knownHostsFile) as f:
                        for l in f.read().split("\n"):
                            if l == address + " " + pubkey:
                                doUpdate = False
                                break
                except FileNotFoundError:
                    pass

                if doUpdate:
                    try:
                        # Remove previous value(s) (without ssk-keygen).
                        with open(knownHostsFile) as f:
                            for l in f.read().split("\n"):
                                if l:
                                    if address + " " not in l: # better using r"^address\ " ?
                                        knownHosts += l + "\n"

                        with open(knownHostsFile, "w") as f:
                            f.write(knownHosts)
                    except FileNotFoundError:
                        pass

                    # Write new value.
                    with open(knownHostsFile, "a") as f:
                        f.write(f"{address} {pubkey}\n")
        except Exception as e:
            raise e
        finally:
            cache.set("knownHosts.lock", False)
