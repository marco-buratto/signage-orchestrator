# -*- mode: ruby -*-
# vi: set ft=ruby :

module OS
    # https://stackoverflow.com/questions/26811089/vagrant-how-to-have-host-platform-specific-provisioning-steps

  def OS.windows?
    (/cygwin|mswin|mingw|bccwin|wince|emx/ =~ RUBY_PLATFORM) != nil
  end

  def OS.mac?
    (/darwin/ =~ RUBY_PLATFORM) != nil
  end

  def OS.unix?
    !OS.windows?
  end

  def OS.linux?
    OS.unix? and not OS.mac?
  end
end

Vagrant.configure("2") do |config|
  config.env.enable # enable vagrant-env(.env).

  Dir.glob('./vagrantfile-*') do |vagrantApiFile|
    eval File.read(vagrantApiFile)
  end
end
