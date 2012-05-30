set apps;
set drives;
set users;
set app_params;
set user_params;
set drive_params;
param applications{i in apps, j in app_params}; 
param phys_drives{i in drives, j in drive_params};
param sys_users{i in users, j in user_params};
var zuzycie{i in drives, j in apps};
maximize uzycie: (sum{i in drives} phys_drives[i, 'size'] * phys_drives[i, 'size'] * 
	(sum{j in apps} zuzycie[i, j])) + (sum{j in apps} applications[j, 'read'] * 
	applications[j, 'prior'] * sum{i in drives} (1 / phys_drives[i, 'read_s'])) + 
	(sum{j in apps} applications[j, 'gen'] * applications[j, 'prior'] * sum{i in drives}
	(1 / phys_drives[i, 'write_s'])); 
subject to zuzycieOd0Do1{i in drives, j in apps}: 0 <= zuzycie[i, j] <= 1;
subject to rozmiarApp{j in apps}: 
    sum{i in drives} (zuzycie[i, j] * phys_drives[i, 'size']) = applications[j, 'gen'] * applications [j, 'time'];
subject to dopasowanie_readLE1{i in drives, j in apps}: 
     zuzycie[i, j] * applications[j, 'read'] / phys_drives[i, 'read_s'] <= zuzycie[i, j]; 
subject to dopasowanie_writeLE1{i in drives, j in apps}: 
     zuzycie[i, j] * applications[j, 'gen'] / phys_drives[i, 'write_s'] <= zuzycie[i, j]; 
