#include <iostream>
#include <vector>
#include <cassert>
#define popcnt(x) __builtin_popcount(x)
using namespace std;


int grid[9][9];
int vis[9][9];

void readGrid(){
	for(int i = 0;i < 9;i++){
		string buffer; cin >> buffer;
		assert(buffer.size() == 9);
		for(int j = 0;j < 9;j++){
			if(buffer[j] == '*') grid[i][j] = (1 << 9) - 1;
			else grid[i][j] = 1 << (buffer[j] - '1');
		}
	}
}

void print(){
	for(int i = 0;i < 9;i++){
		for(int j = 0;j < 9;j++){
			if(popcnt(grid[i][j]) != 1) cout << "*";
			else{
				int k = grid[i][j] & (-grid[i][j]),v = 0;
				while(k != (1 << v)) v++;
				cout << v + 1;
			}
		}
		cout << endl;
	}
}

int select_next(int & oi,int & oj){
	int found_any = 0;
	for(int i = 0;i < 9;i++)
		for(int j = 0;j < 9;j++){
			if(vis[i][j]) continue;
			if(!found_any || popcnt(grid[i][j]) < popcnt(grid[oi][oj])) oi = i,oj = j;
			found_any = 1;
		}
	return found_any;
}

bool set(vector<pair<pair<int,int>,int> > & neighbours,int v){
	for(auto e : neighbours){
		int x = e.first.first,y = e.first.second;
		if(grid[x][y] == (1 << v)) return 0;
	}
	for(auto e : neighbours){
		int x = e.first.first,y = e.first.second;
		grid[x][y] &= ~(1 << v);
	}
	return 1;
}

void unset(vector<pair<pair<int,int>,int> > & neighbours){
	for(auto e : neighbours){
		int x = e.first.first,y = e.first.second;
		grid[x][y] = e.second;
	}
}

vector<pair<pair<int,int>,int> > get_neighbours(int x,int y){
	vector<pair<pair<int,int>,int> > ret;
	for(int i = 0;i < 9;i++)
		if(i != x) ret.push_back({{i,y},grid[i][y]}); // add cells in row
	for(int i = 0;i < 9;i++)
		if(i != y) ret.push_back({{x,i},grid[x][i]}); // add cells in col
	int corner_x = (x/3) * 3,corner_y = (y/3) * 3; // get corners of square;
	for(int i = 0;i < 3;i++)
		for(int j = 0;j < 3;j++){
			if(corner_x + i == x || corner_y + j == y) continue;
			ret.push_back({{corner_x + i,corner_y + j},grid[corner_x + i][corner_y + j]});
		}
	return ret;
}

int num_calls = 0;

int bt(){
	num_calls++;
	int x,y;
	if(!select_next(x,y)) return 1;
	vis[x][y] = 1;
	for(int v = 0;v < 9;v++) // try to put (v + 1) in cell (x,y)
	{
		if(!(grid[x][y] & (1 << v))) continue; // some other cell in row/col/square already took this value
		auto neighbours = get_neighbours(x,y);
		if(!set(neighbours,v)) continue;
		//cerr << "try " << v + 1 << " for " << x << " " << y << endl;
		int tmp = grid[x][y]; grid[x][y] = 1 << v;
		if(bt()) return 1;
		unset(neighbours);
		grid[x][y] = tmp;
	}
	vis[x][y] = 0;
	return 0;
}

int main(){
	readGrid();
	if(bt()) print();
	else cout << "new solution found" << endl;
	cerr << "finished after " << num_calls << endl;
	return 0;
}
