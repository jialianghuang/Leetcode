public class Solution {
    public boolean isPalindrome(int x) {
        if (x<0)
        {
            return false;
        }
        else
        {   int len;
        for(len=1;(x/len)>=10;len=len*10);
        int a,b;
        while(x!=0)
        {
            a=x/len;
            b=x%10;
            if(a!=b)
            {return false;}
            else
            {
                x=(x%len)/10;
                len=len/100;
            }
        
            
        }
        return true;
        }
    }
}
