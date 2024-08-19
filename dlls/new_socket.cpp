#include "new_socket.hpp"

int main(){
    setlocale(LC_ALL, "Russian");
    SetConsoleOutputCP(CP_UTF8);
    return 0;
}

extern "C" __declspec(dllexport) int msg_value(const LPCSTR sometext, const LPCSTR title)
{
    return MessageBoxA(0, sometext, title, MB_YESNO);
}
