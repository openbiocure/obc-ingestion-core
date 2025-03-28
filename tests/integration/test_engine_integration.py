    # Create first scope
    scope1 = initialized_engine.create_scope()
    service1 = scope1.resolve(ScopedService)
    
    # Create second scope
    scope2 = initialized_engine.create_scope()
    service2 = scope2.resolve(ScopedService)
    
    # Services should be different instances
    assert service1 is not service2
    
    # Increment counters
    assert service1.increment() == 1
    assert service1.increment() == 2
    
    # Second service should have separate counter
    assert service2.increment() == 1
    
    # Clean up
    await scope1.dispose()
    await scope2.dispose()
