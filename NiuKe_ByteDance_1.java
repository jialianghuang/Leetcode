import java.util.Scanner; 
public class Main
{ 
    public static void main(String[] args) 
    { 
        Scanner sc = new Scanner(System.in); 
        int n = sc.nextInt(); 
        int c[] = new int[n];
        for(int i = 0; i < n; i++){
             c[i] = sc.nextInt();
         }
        
        int m = sc.nextInt(); 
        int d[][] = new int[m][3];
        for(int j = 0; j < m ;j++){
            d[j][0] = sc.nextInt();
            d[j][1] = sc.nextInt();
            d[j][2] = sc.nextInt();
        }
        int res = 0;
        for(int k = 0;k < m; k++){
            for(int l = d[k][0]-1; l < d[k][1]-1 ; l++ ){
                if(c[l] == d[k][2])
                    res++;
            }
            System.out.println(res);
            res = 0;
        }
    }
}

/*
输入： 第1行为n代表用户的个数 第2行为n个整数，第i个代表用户标号为i的用户对某类文章的喜好度 第3行为一个正整数q代表查询的组数  第4行到第（3+q）行，每行包含3个整数l,r,k代表一组查询，即标号为l<=i<=r的用户中对这类文章喜好值为k的用户的个数。 数据范围n <= 300000,q<=300000 k是整型
*/
