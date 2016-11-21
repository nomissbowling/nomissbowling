/*
  touch_created_time.c

  gcc -m32 -o touch_created_time.exe touch_created_time.c

  ctime = mtime (ignore atime)
*/

#ifndef UNICODE
#define UNICODE
#endif
#include <windows.h>
#include <stdio.h>

int touch_created_time(wchar_t *fn)
{
  int r = 0;
  HANDLE hf = CreateFileW(
    fn,
    GENERIC_WRITE, // FILE_READ_ATTRIBUTES | FILE_WRITE_ATTRIBUTES,
    0,
    NULL,
    OPEN_EXISTING,
    0, // FILE_FLAG_BACKUP_SEMANTICS,
    NULL);
  if(hf == INVALID_HANDLE_VALUE){
    fprintf(stderr, "cannot open file");
    r = 2;
  }else{
    FILETIME ft;
    if(!GetFileTime(hf, NULL, NULL, &ft)){ // p2: atime, p3: mtime
      fprintf(stderr, "cannot get filetime");
      r = 3;
    }else{
      if(!SetFileTime(hf, &ft, NULL, NULL)){ // p1: ctime
        fprintf(stderr, "cannot set filetime");
        r = 4;
      }
    }
    CloseHandle(hf);
  }
  return r;
}

int main(int ac, char **av)
{
  int r;
  int wargc;
  wchar_t **wargv = CommandLineToArgvW(GetCommandLine(), &wargc);
  if(!wargv || wargc < 2){
    fprintf(stderr, "Usage: %s filename", av[0]);
    r = 1;
  }else{
    r = touch_created_time(wargv[1]);
  }
  if(wargv) LocalFree(wargv);
  return r;
}
