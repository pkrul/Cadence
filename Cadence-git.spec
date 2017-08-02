
%global         usegit    1
%global         rpmrel    3

%global         githash   e91750e39acb119cf97f8105a7acc28a8901a4e2
%global         shorthash %(TMP=%githash ; echo ${TMP:0:7})
%global         gitdate   20170707

%if 0%{?usegit} >= 1
%global         srcver    %{gitdate}.git%{shorthash}
%else
%global         srcver    %{rpmrel}
%endif

%define         debug_package %{nil}

Name:		Cadence
Version:	0.8.1
Release:	%{srcver}.auxio%{?dist}
Summary:	Cadence controls and monitors various Linux sound systems

Group:		Applications/Multimedia
License:	GPLv2+
URL:		kxstudio.linuxaudio.org/Applications:%{name}
Source0:        https://github.com/falkTX/%{name}/archive/%{githash}.tar.gz#/%{name}-%{version}-%{gitdate}.git%{shorthash}.tar.gz

Provides:       cadence = %{version}
Provides:       cadence = %{version}-%{release}

BuildRequires:  make
BuildRequires:  gcc-c++
BuildRequires:  expat
BuildRequires:  libuuid-devel
BuildRequires:  freetype-devel
BuildRequires:  glib2-devel
BuildRequires:  qt-devel >= 4
BuildRequires:  PyQt4-devel
BuildRequires:  python3-PyQt4-devel
BuildRequires:	jack-audio-connection-kit-devel

Requires:       kde-filesystem >= 4
Requires:       xorg-x11-xinit
Requires:       qt >= 4.8
Requires:       qt-x11 >= 4.8
Requires:       python3 >= 3.2
Requires:       python3-dbus
Requires:       python3-PyQt4
Requires:       PyQt4
Requires:       zlib
Requires:       bzip2-libs
Requires:       libpng
Requires:       libuuid
Requires:       libstdc++
Requires:       gtk2
Requires:       hicolor-icon-theme
Requires:       desktop-file-utils
Requires:       jack-audio-connection-kit
Requires:       jack-audio-connection-kit-dbus
Requires:       jack_capture
Requires:       pulseaudio-module-jack
Requires:       a2jmidid
Requires:       ladish >= 2

Patch0:         Cadence-0.8.1-paths-plugins-tmp.diff

%description
Cadence is a managed set of re-usable tools, used in audio production.

Cadence               - The main app. It performs system checks, manages JACK,
                        calls other tools and makes system tweaks.
Cadence-JackMeter     - Digital peak meter for JACK.
Cadence-JackSettings  - Simple and easy-to-use configure dialog for jackdbus.
Cadence-Logs          - Small tool that shows JACK, A2J, LASH and LADISH logs
                        in a multi-tab window.
Cadence-Render        - Tool to record (or 'render') a JACK project using 
                        jack-capture, controlled by JACK Transport.
Cadence-XY Controller - Simple XY widget that sends and receives data from 
                        JACK MIDI.
Catarina              - A Patchbay creation/testing/storing app.
Catia                 - A JACK Patchbay, with some neat features like A2J 
                        bridge support and JACK Transport.
Claudia               - LADISH frontend, just like Catia, but focused at 
                        session management through LADISH.
Claudia-Launcher      - A multimedia application launcher with LADISH support.

It is developed by falkTX, using Python3 and Qt4 (and some C++ where needed).

%prep
%setup -qn %{name}-%{version}-%{gitdate}.git%{shorthash}

%patch0 -p1 -b .pluginpaths

%build
make

%install
make install PREFIX=%{_prefix} DESTDIR=%{buildroot}


%post
update-desktop-database -q
touch --no-create %{_datadir}/icons/hicolor/scalable/apps/ >&/dev/null || :

%postun
update-desktop-database -q
if [ $1 -eq 0 ]; then
  touch --no-create %{_datadir}/icons/hicolor/scalable/apps >&/dev/null || :
  gtk-update-icon-cache %{_datadir}/icons/hicolor/scalable/apps >&/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor.scalable/apps &>/dev/null || :

%files
%defattr(-,root,root,-)
%license COPYING
%doc INSTALL.md README.md TODO
%{_bindir}/cadence
%{_bindir}/cadence-aloop-daemon
%{_bindir}/cadence-jackmeter
%{_bindir}/cadence-jacksettings
%{_bindir}/cadence-logs
%{_bindir}/cadence-pulse2jack
%{_bindir}/cadence-pulse2loopback
%{_bindir}/cadence-render
%{_bindir}/cadence-session-start
%{_bindir}/cadence-xycontroller
%{_bindir}/catarina
%{_bindir}/catia
%{_bindir}/claudia
%{_bindir}/claudia-launcher
%{_sysconfdir}/xdg/autostart/*.desktop
%{_sysconfdir}/X11/xinit/xinitrc.d/61cadence-session-inject
%dir %{_datadir}/cadence
%dir %{_datadir}/cadence/icons
%dir %{_datadir}/cadence/icons/claudia-hicolor
%dir %{_datadir}/cadence/icons/claudia-hicolor/16x16
%dir %{_datadir}/cadence/icons/claudia-hicolor/48x48
%dir %{_datadir}/cadence/icons/claudia-hicolor/16x16/apps
%dir %{_datadir}/cadence/icons/claudia-hicolor/48x48/apps
%dir %{_datadir}/cadence/src
%dir %{_datadir}/cadence/templates
%dir %{_datadir}/cadence/pulse2jack
%dir %{_datadir}/cadence/pulse2loopback
%{_datadir}/cadence/icons/claudia-hicolor/*.theme
%{_datadir}/cadence/icons/claudia-hicolor/16x16/apps/*.png
%{_datadir}/cadence/icons/claudia-hicolor/48x48/apps/*.png
%{_datadir}/cadence/src/*.py*
%{_datadir}/cadence/templates/*
%{_datadir}/cadence/pulse2jack/*
%{_datadir}/cadence/pulse2loopback/*
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/16x16/apps/*.png
%{_datadir}/icons/hicolor/48x48/apps/*.png
%{_datadir}/icons/hicolor/128x128/apps/*.png
%{_datadir}/icons/hicolor/256x256/apps/*.png
%{_datadir}/icons/hicolor/scalable/apps/*.svg


%changelog
* Fri Jul 28 2017 Pieter Krul <pkrul@auxio.org> - 0.8.1-20170707-gite91750e
- Initial package build

