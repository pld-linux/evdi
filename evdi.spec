#
# Conditional build:
%bcond_without	kernel		# kernel module
%bcond_without	userspace	# userspace libraries
%bcond_without	python3		# CPython 3.x module

%if 0%{?_pld_builder:1} && %{with kernel} && %{with userspace}
%{error:kernel and userspace cannot be built at the same time on PLD builders}
%endif

Summary:	Extensible Virtual Display Interface library
Summary(pl.UTF-8):	Biblioteka Extensible Virtual Display Interface
Name:		evdi
Version:	1.14.1
%define	rel	1
Release:	%{rel}
License:	LGPL v2.1 (library), GPL v2 (kernel module), MIT (the rest)
Group:		Libraries
#Source0Download: https://github.com/DisplayLink/evdi/releases
Source0:	https://github.com/DisplayLink/evdi/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	282107fc6b2bd75fdeaae2fa2c674eb1
URL:		https://github.com/DisplayLink/evdi
%if %{with userspace}
BuildRequires:	libdrm-devel
BuildRequires:	pkgconfig
%if %{with python3}
BuildRequires:	libstdc++-devel >= 6:4.7
BuildRequires:	python3-devel >= 1:3.8
BuildRequires:	python3-pybind11
BuildRequires:	rpm-pythonprov
%endif
%endif
%if %{with kernel}
%{expand:%buildrequires_kernel kernel%%{_alt_kernel}-module-build >= 3:4.15}
%{expand:%buildrequires_kernel kernel%%{_alt_kernel}-module-build < 3:6.6}
BuildRequires:	rpmbuild(macros) >= 1.701
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%if %{without userspace}
%define		_enable_debug_packages	0
%endif

%description
The Extensible Virtual Display Interface (EVDI) is a Linux kernel
module that enables management of multiple screens, allowing
user-space programs to take control over what happens with the image.
It is essentially a virtual display you can add, remove and receive
screen updates for, in an application that uses the libevdi library.

%description -l pl.UTF-8
EVDI (Extensible Virtual Display Interface) to moduł jądra
umożliwający zarządzanie wieloma ekranami, pozwalając programom w
przestrzeni użytkownika przejmować kontrolę nad obrazen. Jest to
zasadniczo wirtualny wyświetlacz, na którym można dodawać, usuwać i
odbierać uaktualnienia ekranu z poziomu aplikacji wykorzystującej
bibliotekę libevdi.

%package devel
Summary:	Header files for evdi library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki evdi
License:	LGPL v2.1
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for evdi library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki evdi.

%package -n python3-pyevdi
Summary:	Python interface to evdi library
Summary(pl.UTF-8):	Interfejs Pythona do biblioteki evdi
License:	MIT
Group:		Libraries/Python
Requires:	python3-libs >= 1:3.8

%description -n python3-pyevdi
Python interface to evdi library.

%description -n python3-pyevdi -l pl.UTF-8
Interfejs Pythona do biblioteki evdi.

%define	kernel_pkg()\
%package -n kernel%{_alt_kernel}-drm-evdi\
Summary:	Linux driver for Extensible Virtual Display Interface\
Summary(pl.UTF-8):	Sterownik dla Linuksa do Extensible Virtual Display Interface\
Release:	%{rel}@%{_kernel_ver_str}\
Group:		Base/Kernel\
Requires(post,postun):	/sbin/depmod\
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
\
%description -n kernel%{_alt_kernel}-drm-evdi\
Linux driver for Extensible Virtual Display Interface.\
\
%description -n kernel%{_alt_kernel}-drm-evdi -l pl.UTF-8\
Sterownik dla Linuksa do Extensible Virtual Display Interface.\
\
%if %{with kernel}\
%files -n kernel%{_alt_kernel}-drm-evdi\
%defattr(644,root,root,755)\
%dir /lib/modules/%{_kernel_ver}/kernel/drivers/gpu/drm/evdi\
/lib/modules/%{_kernel_ver}/kernel/drivers/gpu/drm/evdi/*.ko*\
%endif\
\
%post	-n kernel%{_alt_kernel}-drm-evdi\
%depmod %{_kernel_ver}\
\
%postun	-n kernel%{_alt_kernel}-drm-evdi\
%depmod %{_kernel_ver}\
%{nil}

%define build_kernel_pkg()\
%build_kernel_modules -m evdi\
\
%install_kernel_modules -D installed -m evdi -d kernel/drivers/gpu/drm/evdi\
%{nil}

%{?with_kernel:%{expand:%create_kernel_packages}}

%prep
%setup -q

%build
%if %{with kernel}
cd module
%{expand:%build_kernel_packages}
cd ..
%endif

%if %{with userspace}
CC="%{__cc}" \
CFLAGS="%{rpmcflags} %{rpmcppflags} -Wextra -Wall -Wno-error=missing-field-initializers -Werror=sign-compare -Wmissing-prototypes -Wstrict-prototypes -Werror=discarded-qualifiers" \
%{__make} -C library

%if %{with python3}
CXX="%{__cxx}" \
CXXFLAGS="%{rpmcxxflags} %{rpmcppflags} -Wextra -Wall -Wno-error=missing-field-initializers -Werror=sign-compare" \
%{__make} -C pyevdi
%endif
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT

%if %{with kernel}
cp -a module/installed/* $RPM_BUILD_ROOT
%endif

%if %{with userspace}
%{__make} -C library install \
	DESTDIR=$RPM_BUILD_ROOT \
	LIBDIR=%{_libdir}

install -d $RPM_BUILD_ROOT{%{_includedir},%{_pkgconfigdir}}
cp -p library/evdi_lib.h $RPM_BUILD_ROOT%{_includedir}

cat >$RPM_BUILD_ROOT%{_pkgconfigdir}/evdi.pc <<'EOF'
prefix=%{_prefix}
libdir=%{_libdir}
includedir=%{_includedir}

Name: evdi
Description: Extensible Virtual Display Interface library
Version: %{version}
Libs: -L${libdir} -levdi
Cflags: -I${includedir}
EOF

%if %{with python3}
%{__make} -C pyevdi install \
	DESTDIR=$RPM_BUILD_ROOT \
	LIBDIR=%{py3_sitedir}
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README.md
%attr(755,root,root) %{_libdir}/libevdi.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libevdi.so.1

%files devel
%defattr(644,root,root,755)
%doc docs/*.md
%attr(755,root,root) %{_libdir}/libevdi.so
%{_includedir}/evdi_lib.h
%{_pkgconfigdir}/evdi.pc

%if %{with python3}
%files -n python3-pyevdi
%defattr(644,root,root,755)
%attr(755,root,root) %{py3_sitedir}/PyEvdi.cpython-*.so*
%endif
%endif
