#
# TODO:
#	-	fix klibc loader crash:
#		http://www.zytor.com/pipermail/klibc/2005-September/001150.html
#
# Conditional build:
%bcond_without	dist_kernel	# build without distribution kernel-headers
#
Summary:	Minimalistic libc subset for use with initramfs
Summary(pl):	Zminimalizowany podzbi�r biblioteki C do u�ywania z initramfs
Name:		klibc
Version:	1.1.1
Release:	1
License:	BSD/GPL
Group:		Libraries
Source0:	http://www.kernel.org/pub/linux/libs/klibc/Testing/%{name}-%{version}.tar.bz2
# Source0-md5:	baa1f6e0b6acbf9576bb28cca5c32c89
Patch0:		%{name}-ksh-quotation.patch
Patch1:		%{name}-klcc.patch
Patch2:		%{name}-fstype_jfs.patch
Patch3:		%{name}-ksh-syntax.patch
URL:		http://www.zytor.com/mailman/listinfo/klibc/
%{?with_dist_kernel:BuildRequires:	kernel-headers >= 2.4}
BuildRequires:	rpmbuild(macros) >= 1.153
BuildRequires:	perl-base
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		no_install_post_strip	1

%description
klibc, what is intended to be a minimalistic libc subset for use with
initramfs. It is deliberately written for small size, minimal
entaglement and portability, not speed. It is definitely a work in
progress, and a lot of things are still missing.

%description -l pl
klibc w zamierzeniu ma by� minimalistycznym podzbiorem biblioteki libc
do u�ycia z initramfs. Celem jest minimalizacja, przeno�no�� ale nie
szybko��. klibc jest rozwijan� bibliotek� w zwi�zku z czym nadal
brakuje wielu rzeczy.

%package devel
Summary:	Development files for klibc
Summary(pl):	Pliki dla programist�w klibc
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	binutils
%{?with_dist_kernel:Requires:	kernel-headers >= 2.4}

%description devel
Small libc for building embedded applications - development files.

%description devel -l pl
Ma�a libc do budowania aplikacji wbudowanych - pliki dla programist�w.

%package static
Summary:	Static klibc libraries
Summary(pl):	Biblioteki statyczne klibc
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static klibc libraries.

%description static -l pl
Biblioteki statyczne klibc.

%package utils-shared
Summary:	Utilities dynamically linked with klibc
Summary(pl):	Narz�dzia dynamicznie zlinkowane z klibc
Group:		Base
Requires:	%{name} = %{version}-%{release}

%description utils-shared
Utilities dynamically linked with klibc.

%description utils-shared -l pl
Narz�dzia dynamicznie zlinkowane z klibc.

%package utils-static
Summary:	Utilities statically linked with klibc
Summary(pl):	Narz�dzia statycznie zlinkowane z klibc
Group:		Base

%description utils-static
Utilities staticly linked with klibc.

%description utils-static -l pl
Narz�dzia statycznie zlinkowane z klibc.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p0
%patch3 -p1

%build
cd include
rm -rf asm asm-generic linux
ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} .
ln -sf asm-%{_target_base_arch} asm
ln -sf %{_kernelsrcdir}/include/asm-generic .
ln -sf %{_kernelsrcdir}/include/linux .
%if %{with dist_kernel}
[ ! -d arch/%{_target_base_arch}/linux ] && mkdir arch/%{_target_base_arch}/linux
ln -sf  %{_kernelsrcdir}/include/linux/autoconf-up.h arch/%{_target_base_arch}/linux/autoconf.h
%endif
for a in `ls arch`; do [ "$a" != "%{_target_base_arch}" ] && rm -rf arch/$a; done
cd ..

%{__make} \
	ARCH=%{_target_base_arch} \
	CC="%{__cc}" \
	prefix=%{_prefix} \
	bindir=%{_bindir} \
	includedir=%{_includedir}/klibc \
	libdir=%{_libdir} \
	SHLIBDIR=/%{_lib} \
	OPTFLAGS="%{rpmcflags} -Os -fomit-frame-pointer -falign-functions=0 \
		-falign-jumps=0 -falign-loops=0 -ffreestanding"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/%{_lib}
install -d $RPM_BUILD_ROOT%{_includedir}/klibc
install -d $RPM_BUILD_ROOT%{_libdir}/klibc/bin-{shared,static}

cp -a include/* $RPM_BUILD_ROOT%{_includedir}/klibc
install klcc -D $RPM_BUILD_ROOT%{_bindir}/klcc
install klcc.1 -D $RPM_BUILD_ROOT%{_mandir}/man1/klcc.1
install klibc/libc.* klibc/crt0.o klibc/interp.o $RPM_BUILD_ROOT%{_libdir}/klibc
install klibc/klibc-*.so $RPM_BUILD_ROOT/%{_lib}
install utils/shared/* $RPM_BUILD_ROOT%{_libdir}/klibc/bin-shared
install utils/static/* $RPM_BUILD_ROOT%{_libdir}/klibc/bin-static

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) /%{_lib}/klibc*.so

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/klcc
%{_includedir}/klibc
%dir %{_libdir}/klibc
%attr(755,root,root) %{_libdir}/klibc/*.so
%{_libdir}/klibc/*.o
%{_mandir}/man1/*

%files static
%defattr(644,root,root,755)
%{_libdir}/klibc/*.a

%files utils-shared
%defattr(644,root,root,755)
%dir %{_libdir}/klibc/bin-shared
%attr(755,root,root) %{_libdir}/klibc/bin-shared/*

%files utils-static
%defattr(644,root,root,755)
%dir %{_libdir}/klibc/bin-static
%attr(755,root,root) %{_libdir}/klibc/bin-static/*
