#include <iostream>
#include <windows.h> 

int main();

extern "C" __declspec(dllexport) int msg_value(const LPCSTR sometext, const LPCSTR title);