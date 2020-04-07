int add(int i1,int i2){
	return i1+i2;
}
int mul(int i1,int i2){
	int res = 0;
	for(int i  =0;i < i2;i++)
		res = add(res,i1);
	return res;
}

int main(){
	int o = 2;
	int p = 6;
	o = mul(o,p);
	return 0;
}
