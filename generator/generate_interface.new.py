#!/bin/python
import json
import string
import os, sys
from pprint import pprint
from generator import generator

#Wrapper_Preload_C Wrapper_Preload_Fortran 
#Wrapper_Interface_C Wrapper_Interface_Fortran
#Interface_C Interface_Fortran

def usage():
	print 'python generate.py [options]'
	print 'This script generate by default the preload and interface file in ./preload/gen and ./interface/gen'
	print 'Options:'
	print '\t --help \t print this message'
	print '\t --only \t generate only the provided file:'
	print '\t\t\t\t Wrapper_Preload_C'
	print '\t\t\t\t Wrapper_Preload_Fortran'
	print '\t\t\t\t Wrapper_Interface_C'
	print '\t\t\t\t Wrapper_Interface_Fortran'
	print '\t\t\t\t Interface_C'
	print '\t\t\t\t Interface_Fortran'

def header_license_file():
	string='//############################# Wi4MPI License ###########################'+'\n'
	string=string+'//# `04/04/2016`                                                         #'+'\n'
	string=string+'//# Copyright or (C) or Copr. Commissariat a l\'Energie Atomique         #'+'\n'
	string=string+'//#                                                                      #'+'\n'
	string=string+'//# IDDN.FR.001.210022.000.S.P.2014.000.10800                            #'+'\n'
	string=string+'//# This file is part of the Wi4MPI library.                             #'+'\n'
	string=string+'//#                                                                      #'+'\n'
	string=string+'//# This software is governed by the CeCILL-C license under French law   #'+'\n'
	string=string+'//# and abiding by the rules of distribution of free software. You can   #'+'\n'
	string=string+'//# use, modify and/ or redistribute the software under the terms of     #'+'\n'
	string=string+'//# the CeCILL-C license as circulated by CEA, CNRS and INRIA at the     #'+'\n'
	string=string+'//# following URL http://www.cecill.info.                                #'+'\n'
	string=string+'//#                                                                      #'+'\n'
	string=string+'//# The fact that you are presently reading this means that you have     #'+'\n'
	string=string+'//# had knowledge of the CeCILL-C license and that you accept its        #'+'\n'
	string=string+'//# terms.                                                               #'+'\n'
	string=string+'//#                                                                      #'+'\n'
	string=string+'//# Authors:                                                             #'+'\n'
	string=string+'//#   - Delforge Tony <tony.delforge.tgcc@cea.fr>                        #'+'\n'
	string=string+'//#   - Ducrot Vincent <vincent.ducrot.tgcc@cea.fr>                      #'+'\n'
	string=string+'//#                                                                      #'+'\n'
	string=string+'//########################################################################'+'\n'
	
	string=string+'/*'+'\n'
	string=string+' * This code is full generated'+'\n'
	string=string+' */'+'\n'
	return string

def generate_wrapper_c(object_gen, wrapper, ompi_const, not_generated, def_list, data, init_conf,not_generated_ptr):
	string=header_license_file()
	string=string+'#ifndef _GNU_SOURCE'+'\n'
	string=string+'#define _GNU_SOURCE'+'\n'
	string=string+'#endif\n'
	string=string+'#include <stdio.h>'+'\n'
	string=string+'#include <dlfcn.h>'+'\n'
	string=string+"/*ompi constante*/"+'\n'
	if not wrapper:
		string=string+ '#if defined(OMPI_OMPI)'+'\n'
		for i in ompi_const:
			string=string+ 'extern '+i.split('[')[0]+';'+'\n'
		string=string+ '#endif'+'\n'	
	ompi_const.seek(0,0)
	string=string+ '#if defined(OMPI_INTEL)'+'\n'
	for i in ompi_const:
		string=string+ i
	string=string+ '#endif'+'\n\n'
	string=string+ '#define EXTERN_ALLOCATED 1\n'
	string=string+ '#include "mappers.h"\n\n'
	string=string+ '__thread int in_w=0;\n'
	for i in not_generated:
		string=string+ i
	for i in data:
		if i['name'] in def_list:
			string=string+object_gen.print_symbol_c(i,name_arg=True,retval_name=False,type_prefix='A_')+';\n'
			string=string+object_gen.print_symbol_c(i,func_ptr=True,prefix='LOCAL_',type_prefix='R_')+';\n\n'
			if wrapper:
				string=string+object_gen.generate_func_asmK_tls(i)+'\n'
			else:
				string=string+object_gen.generate_func_asmK_tls_updated_for_interface(i)+'\n'
			string=string+object_gen.generate_func_c(i, init_conf, app_side=True)+'\n'
			string=string+object_gen.generate_func_c(i, init_conf, app_side=False)+'\n'
	string=string+'#ifdef OMPI_OMPI\n'	
	for list_other in data:
		if list_other['name'] in c2f_list:
			string=string+object_gen.print_symbol(list_other,name_arg=True,retval_name=False,type_prefix='A_')+';'
			string=string+object_gen.print_symbol(list_other,func_ptr=True,prefix='LOCAL_',type_prefix='R_')+';\n'
			string=string+object_gen.generate_func_asmK_tls(list_other)
			string=string+object_gen.generate_func(list_other,init_conf)
			string=string+object_gen.generate_func_r(list_other)
	string=string+'#endif\n'
	string=string+'__attribute__((constructor)) void wrapper_init(void) {\n'
	string=string+'void *lib_handle=dlopen(getenv(\"WI4MPI_RUN_MPI_C_LIB\"),RTLD_NOW|RTLD_GLOBAL);\n'	
	for i in not_generated_ptr:
		string=string+i
	for i in data:
		if i['name'] in def_list or i['name'] in c2f_list:
			string=string+object_gen.load_symbol(i,'lib_handle')+'\n'
	string=string+'#if defined(INTEL_OMPI) || defined(OMPI_INTEL)\n'
	string=string+'local_MPIR_Dup_fn=dlsym(lib_handle,"MPIR_Dup_fn");\n'
	string=string+'#endif\n'
	if wrapper:
		string=string+'#if defined(INTEL_INTEL) || defined(OMPI_INTEL)\n'
		string=string+'R_MPI_UNWEIGHTED=dlsym(lib_handle,"MPI_UNWEIGHTED");\n'
		string=string+'R_MPI_WEIGHTS_EMPTY=dlsym(lib_handle,"MPI_WEIGHTS_EMPTY");\n'
		string=string+'#endif\n'
		string=string+'#if defined(INTEL_INTEL) || defined(INTEL_OMPI)\n'
		string=string+'A_MPI_UNWEIGHTED=dlsym(lib_handle,"MPI_UNWEIGHTED");\n'
		string=string+'A_MPI_WEIGHTS_EMPTY=dlsym(lib_handle,"MPI_WEIGHTS_EMPTY");\n'
		string=string+'#endif\n'
		string=string+'//#ifdef OMPI_OMPI\n'
		string=string+'//init_global(lib_handle);\n'
		string=string+'//#endif\n'
	else:
		string=string+'#ifdef OMPI_OMPI\n'
		string=string+'init_global(lib_handle);\n'
		string=string+'#elif OMPI_INTEL\n'
		string=string+'R_MPI_UNWEIGHTED=dlsym(lib_handle,"MPI_UNWEIGHTED");\n'
		string=string+'R_MPI_WEIGHTS_EMPTY=dlsym(lib_handle,"MPI_WEIGHTS_EMPTY");\n'
		string=string+'MPI_UNWEIGHTED=dlsym(lib_handle,"MPI_UNWEIGHTED");\n'
		string=string+'MPI_WEIGHTS_EMPTY=dlsym(lib_handle,"MPI_WEIGHTS_EMPTY");\n'
		string=string+'#endif\n'
	for conf in init_conf:
		string=string+conf
	string=string+'}'
	return string

def generate_wrapper_f(object_gen, data_f, data_f_overide, wrapper):
	string=header_license_file()
	#overiding json dictionary
	for idx,j in enumerate(data_f):
		for i in data_f_overide:
			if i['name'] == j['name']:
				data_f[idx]=i
	string=string+' #include <stdlib.h>'+'\n'
	string=string+' #include <stdio.h>'+'\n'
	string=string+'#include <dlfcn.h>'+'\n'
	string=string+'#include "wrapper_f.h"'+'\n'
	string=string+'extern __thread int in_w;'+'\n'
	for i in data_f:
		for j in def_list_f:
			if i['name'].lstrip().rstrip() == j.lstrip().rstrip():
				string=string+object_gen.print_symbol_f(i,app_side=True,func_ptr=False,prefix='',postfix='_',type_prefix='R_',lower=True)+';\n\n'
				string=string+object_gen.print_symbol_f(i,app_side=True,func_ptr=False,prefix='',postfix='__',type_prefix='R_',lower=True)+';\n\n'
				string=string+object_gen.print_symbol_f(i,app_side=True,func_ptr=False,prefix='p',postfix='_',type_prefix='R_',lower=True)+';\n\n'
				string=string+object_gen.print_symbol_f(i,app_side=True,func_ptr=False,prefix='p',postfix='__',type_prefix='R_',lower=True)+';\n\n'
				string=string+object_gen.print_symbol_f(i,app_side=True,func_ptr=False,prefix='p',postfix='_',type_prefix='R_',lower=True)+';\n\n'
				if wrapper:
					string=string+'#define A_f_'+i['name'] +' _P'+i['name']+'\n'
				else:
					string=string+'//#define A_f_'+i['name'] +' _P'+i['name']+'\n'
				string=string+'#pragma weak '+i['name'].lower()+'_=_P'+i['name']+'\n'
				string=string+'#pragma weak '+i['name'].lower()+'__=_P'+i['name']+'\n'
				string=string+'#pragma weak p'+i['name'].lower()+'__=_P'+i['name']+'\n'
				string=string+object_gen.print_symbol_f(i,app_side=True,func_ptr=True,prefix='_LOCAL_',type_prefix='R_')+';\n\n'
				string=string+object_gen.generate_func_f(i)+'\n'
	string=string+'__attribute__((constructor)) void wrapper_init_f(void) {\n'
	if not wrapper:
		string=string+'void *lib_handle_f=dlopen(getenv(\"WI4MPI_RUN_MPI_F_LIB\"),RTLD_NOW|RTLD_GLOBAL);\n'
	for i in data_f:
		for j in def_list_f:
			if i['name'].lstrip().rstrip() == j.lstrip().rstrip():
				if wrapper:
					string=string+object_gen.load_symbol(i,'RTLD_NEXT')+'\n'
				else:
					string=string+object_gen.load_symbol(i,'lib_handle_f')+'\n'
	if wrapper:
		string=string+object_gen.load_symbol({'name':'MPI_Error_string'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Get_processor_name'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_File_open'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_File_set_view'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_File_get_view'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_File_delete'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Info_delete'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Info_get'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Info_get_nthkey'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Info_get_valuelen'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Info_set'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Win_get_name'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Win_set_name'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Comm_get_name'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Comm_set_name'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Comm_spawn'},'RTLD_NEXT')+'\n'
		#string=string+object_gen.load_symbol({'name':'MPI_Comm_spawn_multiple'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Type_get_name'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Type_set_name'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Add_error_string'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Close_port'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Get_library_version'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Open_port'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Publish_name'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Unpublish_name'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Lookup_name'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Pack_external'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Pack_external_size'},'RTLD_NEXT')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Unpack_external'},'RTLD_NEXT')+'\n'
	else:
		string=string+object_gen.load_symbol({'name':'MPI_Error_string'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Get_processor_name'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_File_open'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_File_set_view'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_File_get_view'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_File_delete'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Info_delete'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Info_get'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Info_get_nthkey'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Info_get_valuelen'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Info_set'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Win_get_name'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Win_set_name'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Comm_get_name'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Comm_set_name'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Comm_spawn'},'lib_handle_f')+'\n'
		#string=string+object_gen.load_symbol({'name':'MPI_Comm_spawn_multiple'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Type_get_name'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Type_set_name'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Add_error_string'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Close_port'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Get_library_version'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Open_port'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Publish_name'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Unpublish_name'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Lookup_name'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Pack_external'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Pack_external_size'},'lib_handle_f')+'\n'
		string=string+object_gen.load_symbol({'name':'MPI_Unpack_external'},'lib_handle_f')+'\n'

		string=string+'#ifdef ompi_ompi\n'
		string=string+'ccc_mpi_fortran_bottom_=dlsym(lib_handle_f,"mpi_fortran_bottom_");'+'\n'
		string=string+'ccc_mpi_fortran_in_place_=dlsym(lib_handle_f,"mpi_fortran_in_place_");'+'\n'
		string=string+'ccc_mpi_fortran_argv_null_=dlsym(lib_handle_f,"mpi_fortran_argv_null_");'+'\n'
		string=string+'ccc_mpi_fortran_argvs_null_=dlsym(lib_handle_f,"mpi_fortran_argvs_null_");'+'\n'
		string=string+'ccc_mpi_fortran_errcodes_ignore_=dlsym(lib_handle_f,"mpi_fortran_errcodes_ignore_");'+'\n'
		string=string+'ccc_mpi_fortran_status_ignore_=dlsym(lib_handle_f,"mpi_fortran_status_ignore_");'+'\n'
		string=string+'ccc_mpi_fortran_statuses_ignore_=dlsym(lib_handle_f,"mpi_fortran_statuses_ignore_");'+'\n'
		string=string+'ccc_mpi_fortran_unweighted_=dlsym(lib_handle_f,"mpi_fortran_unweighted_");'+'\n'
		string=string+'ccc_mpi_fortran_weights_empty_=dlsym(lib_handle_f,"mpi_fortran_weights_empty_");'+'\n'
		string=string+'////mpi_null_delete_fn_;'+'\n'
		string=string+'////mpi_null_copy_fn_;'+'\n'
		string=string+'////mpi_null_delete_fn_;'+'\n'
		string=string+'#endif\n'
		string=string+'#ifdef ompi_mpich\n'
		string=string+'ccc_mpi_fortran_bottom_=dlsym(lib_handle_f,"mpipriv1_");'+'\n'
		string=string+'ccc_mpi_fortran_in_place_=((int *)dlsym(lib_handle_f,"mpipriv1_")+1);'+'\n'
		string=string+'ccc_mpi_fortran_argv_null_=((int*)dlsym(lib_handle_f,"mpiprivc_")+1);'+'\n'
		string=string+'ccc_mpi_fortran_argvs_null_=dlsym(lib_handle_f,"mpiprivc_");'+'\n'
		string=string+'ccc_mpi_fortran_errcodes_ignore_=((int *)dlsym(lib_handle_f,"mpipriv2_")+1);'+'\n'
		string=string+'ccc_mpi_fortran_status_ignore_=((int *)dlsym(lib_handle_f,"mpipriv1_")+2);'+'\n'
		string=string+'ccc_mpi_fortran_statuses_ignore_=dlsym(lib_handle_f,"mpipriv2_");'+'\n'
		string=string+'ccc_mpi_fortran_unweighted_=dlsym(lib_handle_f,"mpifcmb5_");'+'\n'
		string=string+'ccc_mpi_fortran_weights_empty_=dlsym(lib_handle_f,"mpifcmb9_");'+'\n'
		string=string+'#endif\n'
		string=string+'//local_mpi_null_delete_fn_=dlsym(lib_handle_f,"mpi_null_delete_fn_");'+'\n'
		string=string+'//local_mpi_null_copy_fn_=dlsym(lib_handle_f,"mpi_null_copy_fn_");'+'\n'
		string=string+'//local_mpi_dup_fn_=dlsym(lib_handle_f,"mpi_dup_fn_");'+'\n'
	string=string+'}\n'
	return string
	
def generate_interface(object_gen, interface_key_gen, data, def_list, c2f_list,static_list=["OMPI","INTEL"]):
	string=header_license_file()
	string=string+'#define _GNU_SOURCE\n'
	string=string+'#include <stdio.h>\n' 
	string=string+'#include <dlfcn.h>\n' 
	string=string+'#include \"mpi.h\"\n' 
	string=string+"\nchar wi4mpi_mode[]=\"\";\n\n"
	string=string+"/*ompi constante*/\n" 
	for i in interface_key_gen:
		string=string+i
	for i in data:
		if i['name'] in def_list:
			string=string+'\n'+object_gen.print_symbol_c(i,name_arg=True,retval_name=False,type_prefix='',interface=True)+';\n' 
			string=string+'#define '+i['name']+' P'+i['name']+'\n'
			string=string+'#pragma weak '+i['name']+'=P'+i['name']+'\n'
			string=string+object_gen.print_symbol_c(i,func_ptr=True,prefix='INTERFACE_LOCAL_',type_prefix='',interface=True)+';\n'
			string=string+'#ifdef WI4MPI_STATIC\n'
			for j in static_list:
				string=string+'extern '+object_gen.print_symbol_c(i,func_ptr=False,prefix='INTERF_2_'+j+'_A_',type_prefix='',interface=True)+';\n'
			string=string+'#endif /*WI4MPI_STATIC*/\n'
			string=string+'\n'+object_gen.print_symbol_c(i,prefix='P',name_arg=True,retval_name=False,app_side=False,run_side=False,inter_side=True)
			string=string+object_gen.header_func(i,app_side=False)+'\n'
			string=string+object_gen.print_symbol_c(i,prefix='INTERFACE_LOCAL_',name_arg=True,retval_name=True,app_side=False,call=True, r_func=False,type_prefix='',interface=True)+';\n'
			string=string+object_gen.footer_func(i,app_side=False)
	string=string+'\n#ifdef WI4MPI_STATIC\n'
	for j in static_list:
		string=string+'extern int INTERF_2_'+j+'_A_MPI_Keyval_create(void);'
		string=string+'extern int INTERF_2_'+j+'_A_MPI_Keyval_free(void);\n'        
		string=string+'extern int INTERF_2_'+j+'_A_MPI_Comm_create_keyval(void);\n'
		string=string+'extern int INTERF_2_'+j+'_A_MPI_Comm_free_keyval(void);\n'   
		string=string+'extern int INTERF_2_'+j+'_A_MPI_Win_get_attr(void);\n'       
		string=string+'extern int INTERF_2_'+j+'_A_MPI_Win_set_attr(void);\n'       
	string=string+'#endif /*WI4MPI_STATIC*/\n'
	string=string+'\n__attribute__((constructor)) void wrapper_interface(void) {\n'                     
	#string=string+'void *interface_handle=dlopen(getenv(\"WI4MPI_WRAPPER_LIB\"),RTLD_NOW|RTLD_GLOBAL);\n' 
	#string=string+'if(!interface_handle)\n'                                                           
	#string=string+'{\n'                                                                               
	#string=string+'printf("no true IC lib defined\\nerror :%s\\n",dlerror());\n'                      
	#string=string+'exit(1);\n'                                                                        
	#string=string+'}\n'
	string=string+'#ifndef WI4MPI_STATIC\n'
	string=string+'#define to_string(name) #name\n'
	string=string+'#define handle_loader(name)\\\n'
	string=string+'INTERFACE_LOCAL_##name=dlsym(interface_handle,to_string(CC##name))\n'
	string=string+'\n'
	string=string+'#else\n'
	string=string+'#define handle_loader(name,MPI_TARGET)\\\n'
	string=string+'INTERFACE_LOCAL_##name=&MPI_TARGET##name\n'
	string=string+'\n'
	string=string+'#endif /*WI4MPI_STATIC*/\n'
	string=string+'void *interface_handle;\n'
	string=string+'#ifndef WI4MPI_STATIC\nif(getenv(\"WI4MPI_WRAPPER_LIB\") != NULL)\n'
	string=string+'\tinterface_handle=dlopen(getenv("WI4MPI_WRAPPER_LIB"),RTLD_NOW|RTLD_GLOBAL);\n'
	string=string+'else\n'
	string=string+'{\n'
	string=string+'\tif(strcmp(wi4mpi_mode,\"\") != 0)\n'
	string=string+'\t{\n'
	string=string+'\t\tinterface_handle=dlopen(wi4mpi_mode,RTLD_NOW|RTLD_GLOBAL);\n'
	string=string+'\t}\n'
	string=string+'\telse\n'
	string=string+'\t{\n'
	string=string+'\t\tfprintf(stderr,\"Please provide either WI4MPI_WRAPPER_LIB environment or compile with -wi4mpi_default_run_paths\\n\");\n'
	string=string+'\t\texit(1);\n'
	string=string+'\t}\n'
	string=string+'}\n'
	string=string+'if(!interface_handle)\n'
	string=string+'{\n'                                                     
	string=string+'\tprintf("Dlopen failed to open WI4MPI librarie.\\nerror :%s\\n",dlerror());\n'
	string=string+'\texit(1);\n'
	string=string+'}\n'
	string=string+'handle_loader(MPI_Keyval_create);'
	string=string+'handle_loader(MPI_Keyval_free);\n'              
	string=string+'handle_loader(MPI_Comm_create_keyval);\n'
	string=string+'handle_loader(MPI_Comm_free_keyval);\n'    
	string=string+'handle_loader(MPI_Win_get_attr);\n'            
	string=string+'handle_loader(MPI_Win_set_attr);\n'            
	for i in data:                                                                         
		if i['name'] in def_list or i['name'] in c2f_list:                                  
			string=string+'handle_loader('+i['name']+');\n'
	
	string=string+'\n'
	string=string+'#else\n' 
	string=string+'char *target=getenv(\"WI4MPI_STATIC_TARGET_TYPE\");\n'
	for j in static_list:
		string=string+'if(!strcmp(target,\"'+j+'\")){\n'
		string=string+'handle_loader(MPI_Keyval_create,INTERF_2_'+j+'_A_);' 
		string=string+'handle_loader(MPI_Keyval_free,INTERF_2_'+j+'_A_);\n'                                             
		string=string+'handle_loader(MPI_Comm_create_keyval,INTERF_2_'+j+'_A_);\n'
		string=string+'handle_loader(MPI_Comm_free_keyval,INTERF_2_'+j+'_A_);\n'
		string=string+'handle_loader(MPI_Win_get_attr,INTERF_2_'+j+'_A_);\n'
		string=string+'handle_loader(MPI_Win_set_attr,INTERF_2_'+j+'_A_);\n'
		for i in data:                                                                         
			if i['name'] in def_list or i['name'] in c2f_list:                                  
				string=string+'handle_loader('+i['name']+',INTERF_2_'+j+'_A_);\n'
		string=string+'}else{\n'
	string=string+'printf(\"no target library defined conversion cannot be choosen\\n\" );\nexit(1);\n\n'
	for j in static_list:
		string=string+'}\n'
	string=string+'#endif\n'
	string=string+'}\n'                                                                              
	return string

def generate_interface_f(object_gen, data2,data_f,def_list_f,static_list=["OMPI","INTEL"]):
	string=header_license_file()
	for idx,j in enumerate(data_f): 
		for i in data2:              
			if i['name'] == j['name']:
				data_f[idx]=i         
	string=string+'#define _GNU_SOURCE\n'
	string=string+'#include <stdio.h>\n'
	string=string+'#include <dlfcn.h>\n'
	string=string+'#include \"manual_interface.h\"\n'
	string=string+'void *mpi_comm_null_copy_fn_=NULL;\n'
	string=string+'void *mpi_win_dup_fn_=NULL;\n'
	string=string+'void *mpi_null_copy_fn_=NULL;\n'
	string=string+'void *mpi_comm_null_delete_fn_=NULL;\n'
	string=string+'void *mpi_comm_dup_fn_=NULL;\n'
	string=string+'void *mpi_type_null_copy_fn_=NULL;\n'
	string=string+'void *mpi_null_delete_fn_=NULL;\n'
	string=string+'void *mpi_dup_fn_=NULL;\n'
	string=string+'void *mpi_conversion_fn_null_=NULL;\n'
	string=string+'void *mpi_win_null_delete_fn_=NULL;\n'
	string=string+'void *mpi_type_null_delete_fn_=NULL;\n'
	string=string+'void *mpi_type_dup_fn_=NULL;\n'
	string=string+'void *mpi_win_null_copy_fn_=NULL;\n'
	string=string+"/*ompi constante*/\n"
	string=string+"\nchar wi4mpi_mode_f[]=\"\";\n\n"
	for i in data_f:
		for j in def_list_f: 
			if i['name'].lstrip().rstrip() == j.lstrip().rstrip():
				string=string+'void '+object_gen.print_symbol_f(i,name_arg=True,postfix='_',retval_name=False,type_prefix='',lower=True)+';\n'
				string=string+'#pragma weak '+i['name'].lower()+'_=p'+i['name'].lower()+'_\n'
				string=string+'void '+object_gen.print_symbol_f(i,func_ptr=True,prefix='INTERFACE_F_LOCAL_',type_prefix='')+';\n\n'
				string=string+'void p'+object_gen.print_symbol_f(i,name_arg=True,retval_name=False,type_prefix='',lower=True,postfix='_').lstrip()+'{\n\n'
				string=string+'return '+object_gen.print_symbol_f(i,prefix='INTERFACE_F_LOCAL_',type_prefix='',call=True,name_arg=True,direct=True)+';\n}\n\n'
				string=string+'#ifdef WI4MPI_STATIC\n'
				for j in static_list:
					string=string+'extern '+object_gen.print_symbol_f(i,func_ptr=True,prefix='INTERF_2_'+j+'_A_f_',type_prefix='')+';\n'
				string=string+'#endif /*WI4MPI_STATIC*/\n'
	string=string+'#ifdef WI4MPI_STATIC\n'
	for j in static_list:
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Error_string)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Get_processor_name)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_File_open)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_File_set_view)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_File_get_view)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_File_delete)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Info_delete)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Info_get)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Info_get_nthkey)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Info_get_valuelen)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Info_set)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Win_get_name)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Win_set_name)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Comm_spawn)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Comm_get_name)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Comm_set_name)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Type_get_name)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Type_set_name)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Add_error_string)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Close_port)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Get_library_version)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Open_port)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Publish_name)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Unpublish_name)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Lookup_name)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Pack_external)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Pack_external_size)(void);\n'
	    string=string+'extern void (INTERF_2_'+j+'_A_f_MPI_Unpack_external)(void);\n'
		
	string=string+'#endif /*WI4MPI_STATIC*/\n'

	string=string+'__attribute__((constructor)) void wrapper_interface_f(void) {\n'
	#string=string+'void *interface_handle_f=dlopen(getenv(\"WI4MPI_WRAPPER_LIB\"),RTLD_NOW|RTLD_GLOBAL);\n'
	#string=string+'if(!interface_handle_f)\n' 
	#string=string+'{\n'                                    
	#string=string+'printf("no true if lib defined\\nerror :%s\\n",dlerror());\n'
	#string=string+'exit(1);\n'
	#string=string+'}\n'                                                   
	string=string+'#ifndef WI4MPI_STATIC\n'
	string=string+'#define to_string(name) #name\n'
	string=string+'#define handle_loader(name)\\\n'
	string=string+'INTERFACE_F_LOCAL_##name=dlsym(interface_handle,to_string(CC##name))\n'
	string=string+'\n'
	string=string+'#else\n'
	string=string+'#define handle_loader(name,MPI_TARGET)\\\n'
	string=string+'INTERFACE_F_LOCAL_##name=MPI_TARGET##name\n'
	string=string+'\n'
	string=string+'#endif /*WI4MPI_STATIC*/\n'
	string=string+'#ifndef WI4MPI_STATIC\n'
	string=string+'void *interface_handle_f;\n'
	string=string+'if(getenv(\"WI4MPI_WRAPPER_LIB\") != NULL)\n'
	string=string+'{\n'
	string=string+'\tinterface_handle_f=dlopen(getenv("WI4MPI_WRAPPER_LIB"),RTLD_NOW|RTLD_GLOBAL);\n'
	string=string+'}\n'
	string=string+'else\n'
	string=string+'{\n'
	string=string+'\tif(strcmp(wi4mpi_mode_f,\"\") != 0)\n'
	string=string+'\t{\n'
	string=string+'\t\tinterface_handle_f=dlopen(wi4mpi_mode_f,RTLD_NOW|RTLD_GLOBAL);\n'
	string=string+'\t}\n'
	string=string+'\telse\n'
	string=string+'\t{\n'
	string=string+'\t\tfprintf(stderr,\"Please provide either WI4MPI_WRAPPER_LIB environment or compile with -wi4mpi_default_run_paths\\n\");\n'
	string=string+'\t\texit(1);\n'
	string=string+'\t}\n'
	string=string+'}\n'
	string=string+'if(!interface_handle_f)\n'
	string=string+'{\n'                                                     
	string=string+'\tprintf("Dlopen failed to open WI4MPI librarie.\\nerror :%s\\n",dlerror());\n'
	string=string+'\texit(1);\n'
	string=string+'}\n' 
	for i in data_f:
		for j in def_list_f: 
			if i['name'].lstrip().rstrip() == j.lstrip().rstrip():
				string=string+'INTERFACE_F_LOCAL_'+i['name']+'=dlsym(interface_handle_f,\"A_f_'+i['name']+'\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Error_string=dlsym(interface_handle_f, \"A_f_MPI_Error_string\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Get_processor_name=dlsym(interface_handle_f, \"A_f_MPI_Get_processor_name\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_File_open=dlsym(interface_handle_f, \"A_f_MPI_File_open\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_File_set_view=dlsym(interface_handle_f, \"A_f_MPI_File_set_view\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_File_get_view=dlsym(interface_handle_f, \"A_f_MPI_File_get_view\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_File_delete=dlsym(interface_handle_f, \"A_f_MPI_File_delete\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Info_delete=dlsym(interface_handle_f, \"A_f_MPI_Info_delete\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Info_get=dlsym(interface_handle_f, \"A_f_MPI_Info_get\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Info_get_nthkey=dlsym(interface_handle_f, \"A_f_MPI_Info_get_nthkey\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Info_get_valuelen=dlsym(interface_handle_f, \"A_f_MPI_Info_get_valuelen\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Info_set=dlsym(interface_handle_f, \"A_f_MPI_Info_set\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Win_get_name=dlsym(interface_handle_f, \"A_f_MPI_Win_get_name\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Win_set_name=dlsym(interface_handle_f, \"A_f_MPI_Win_set_name\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Comm_get_name=dlsym(interface_handle_f, \"A_f_MPI_Comm_get_name\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Comm_set_name=dlsym(interface_handle_f, \"A_f_MPI_Comm_set_name\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Comm_spawn=dlsym(interface_handle_f, \"A_f_MPI_Comm_spawn\");\n'
	#string=string+'INTERFACE_F_LOCAL_MPI_Comm_spawn_multiple=dlsym(interface_handle_f, \"A_f_MPI_Comm_spawn_multiple\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Type_get_name=dlsym(interface_handle_f, \"A_f_MPI_Type_get_name\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Type_set_name=dlsym(interface_handle_f, \"A_f_MPI_Type_set_name\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Add_error_string=dlsym(interface_handle_f, \"A_f_MPI_Add_error_string\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Close_port=dlsym(interface_handle_f, \"A_f_MPI_Close_port\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Get_library_version=dlsym(interface_handle_f, \"A_f_MPI_Get_library_version\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Open_port=dlsym(interface_handle_f, \"A_f_MPI_Open_port\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Publish_name=dlsym(interface_handle_f, \"A_f_MPI_Publish_name\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Unpublish_name=dlsym(interface_handle_f, \"A_f_MPI_Unpublish_name\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Lookup_name=dlsym(interface_handle_f, \"A_f_MPI_Lookup_name\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Pack_external=dlsym(interface_handle_f, \"A_f_MPI_Pack_external\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Pack_external_size=dlsym(interface_handle_f, \"A_f_MPI_Pack_external_size\");\n'
	string=string+'INTERFACE_F_LOCAL_MPI_Unpack_external=dlsym(interface_handle_f, \"A_f_MPI_Unpack_external\");\n'
	string=string+'#else\n'
	string=string+'char *target=getenv(\"WI4MPI_STATIC_TARGET_TYPE\");\n'
	for k in  static_list:
		string=string+'if(!strcmp(target,\"'+k+'\")){\n'
		for i in data_f:
			for j in def_list_f: 
				if i['name'].lstrip().rstrip() == j.lstrip().rstrip():
				    string=string+'handle_loader('+i['name']+',INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Error_string,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Get_processor_name,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_File_open,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_File_set_view,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_File_get_view,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_File_delete,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Info_delete,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Info_get,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Info_get_nthkey,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Info_get_valuelen,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Info_set,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Win_get_name,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Win_set_name,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Comm_get_name,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Comm_set_name,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Comm_spawn,INTERF_2_'+k+'_A_f_);\n'
		#string=string+'handle_loader(MPI_Comm_spawn_multiple,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Type_get_name,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Type_set_name,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Add_error_string,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Close_port,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Get_library_version,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Open_port,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Publish_name,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Unpublish_name,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Lookup_name,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Pack_external,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Pack_external_size,INTERF_2_'+k+'_A_f_);\n'
		string=string+'handle_loader(MPI_Unpack_external,INTERF_2_'+k+'_A_f_);\n'
		string=string+'}else\n'
	string=string+'{printf(\"no valid WI4MPI_STATIC_TARGET_TYPE defined\\n\");exit(1);}\n'
	string=string+'#endif\n'
	string=string+'}\n'
	return string


if __name__ == '__main__':
#
	  #if len(sys.argv) > 1:
	  #	for i in sys.argv:
	  #		if i == '--help':
	  #				usage()
	  #				sys.exit(1)
	  #		elif i == '--only':
	  #			sys.argv[0]
#Set generation directories
#--------------------------
	interface_directory="./interface/gen"
	if not os.path.exists(interface_directory):
		os.makedirs(interface_directory)

	preload_directory="./preload/gen"
	if not os.path.exists(preload_directory):
		os.makedirs(preload_directory)

	root = os.getcwd()

# Set Common file among the different generation
	#Opening C and Fortran function dictionary
	#-----------------------------------------
	with open('./C/functions.json') as data_file:
	      data_c = json.load(data_file)
	with open('./FORTRAN/functions.json') as data_file_f:
	      data_f = json.load(data_file_f)
	#Opening C and Fortran mapper dictionary
	#---------------------------------------
	with open('./C/mappers.json') as mapper_file:
	      mappers_c=json.load(mapper_file)
	with open('./FORTRAN/mappers_f.json') as mapper_f_file:
	      mappers_f=json.load(mapper_f_file)
	
	#File containing all pre-requisites in __attribute__((constructor)) void wrapper_init()
	#--------------------------------------------------------------------------------------
	init_conf =  open('./C/init_conf.txt','r')
	
	not_generated_ptr = open('./C/not_generated_pointer.txt','r')
	ompi_const=open('./C/ompi_const_set.txt','r')

	#File containing the list of pre_requisites for interop C-Fortran
	#----------------------------------------------------------------
	with open('./C/c2f_f2c_list.txt') as c2f:
		c2f_list=c2f.read().splitlines()

# Sequence generating file
	#Generating Preload file
	#-----------------------
	#File containing all the functions not generated (included code chooser asm)
	print " >>>>> Generating preload/gen/test_generation_wrapper.c"
	wrapper=True
	not_generated = open('./C/not_generated_asmK_tls.txt','r')
	
	C_file='C/func_list_preload_c.txt'
	F_file='FORTRAN/func_list_preload.txt'
	with open(C_file) as fl:
		def_list_c=fl.read().splitlines()
	with open(F_file) as fl_f:
		def_list_f=fl_f.read().splitlines()

	wrapper_preload_c=generator("Wrapper_Preload_C",mappers_c,data_c)
	os.chdir(preload_directory)
	preload_wrapper_c = open("test_generation_wrapper.c", "w")
	string=generate_wrapper_c(wrapper_preload_c, wrapper, ompi_const, not_generated, def_list_c, data_c,init_conf,not_generated_ptr)
	preload_wrapper_c.write(string)
	preload_wrapper_c.close()
	fl.close()
	not_generated.close()
	print "        Done."
	os.chdir(root)
   
	print " >>>>> Generating preload/gen/wrapper.c"
	with open('./FORTRAN/functions_fort_overide.json') as data_file:
		data_f_overide = json.load(data_file)

	wrapper_preload_fortran=generator("Wrapper_Preload_Fortran",mappers_f,data_f)
	os.chdir(preload_directory)
	preload_wrapper_f= open("wrapper.c","w")
	string=generate_wrapper_f(wrapper_preload_fortran, data_f, data_f_overide,wrapper)
	preload_wrapper_f.write(string)
	preload_wrapper_f.close()
	fl_f.close()
	print "        Done."
	os.chdir(root)

	#Generating Interface file
	#-------------------------
	print " >>>>> Generating interface/gen/test_generation_wrapper.c"
	wrapper=False
	not_generated = open('./C/not_generated_asmK_tls_updated_for_interface.txt','r')
	
	C_file='C/func_list_interface_c.txt'
	F_file='FORTRAN/func_list_interface.txt'
	with open(C_file) as fl:
		def_list_c=fl.read().splitlines()
	with open(F_file) as fl_f:
		def_list_f=fl_f.read().splitlines()

	ompi_const.seek(0,0)
	init_conf.seek(0,0)
	not_generated_ptr.seek(0,0)
	wrapper_interface_c=generator("Wrapper_Interface_C", mappers_c,data_c)
	os.chdir(interface_directory)
	interface_wrapper_c =open("test_generation_wrapper.c", "w")
	string=generate_wrapper_c(wrapper_interface_c, wrapper, ompi_const, not_generated, def_list_c, data_c,init_conf,not_generated_ptr)
	interface_wrapper_c.write(string)
	interface_wrapper_c.close()
	fl.close()
	not_generated.close()
	print "        Done."
	os.chdir(root)
	
	print " >>>>> Generating interface/gen/wrapper.c"
	wrapper_interface_fortran=generator("Wrapper_Interface_Fortran",mappers_f,data_f)
	os.chdir(interface_directory)
	interface_wrapper_fortran = open("wrapper.c","w")
	string=generate_wrapper_f(wrapper_interface_fortran, data_f, data_f_overide, wrapper)
	interface_wrapper_fortran.write(string)
	interface_wrapper_fortran.close()
	data_file.close()
	fl_f.close()
	print "        Done."
	os.chdir(root)


	print " >>>>> Generating interface/gen/interface_test.c"
	interface_key_gen=open('./C/not_generated_interface_KEYVAL.txt','r')
	with open('./C/c2f_f2c_list.txt') as c2f:
		c2f_list=c2f.read().splitlines()

	C_file='C/func_list_interface_c_interface.txt'
	F_file='FORTRAN/func_list_interface_interface.text'
	with open(C_file) as fl:
		def_list_c=fl.read().splitlines()
	with open(F_file) as fl_f:
		def_list_f=fl_f.read().splitlines()

	c_interface=generator("Interface_C", mappers_c,data_c)
	os.chdir(interface_directory)
	interface_c= open("interface_test.c","w")
	string=generate_interface(c_interface, interface_key_gen, data_c, def_list_c, c2f_list)
	interface_c.write(string)
	interface_c.close()
	fl.close()
	print "        Done."
	os.chdir(root)

	print " >>>>> Generating interface/gen/interface_fort.c"
	f_interface=generator("Interface_Fortran",mappers_f,data_f)
	#data_f_overide
	os.chdir(interface_directory)
	interface_f=open("interface_fort.c","w")
	string=generate_interface_f(f_interface, data_f_overide, data_f,def_list_f)
	interface_f.write(string)
	interface_f.close()
	fl_f.close()
	os.chdir(root)